from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
import decimal
import io
import base64
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter

from apps.P1_Identidad_Acceso.models import Usuario, TransaccionClinica, NotificacionPush
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita

class MobileCitasAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol != 'PACIENTE':
            return Response({"detail": "Solo pacientes pueden ver su historial móvil."}, status=status.HTTP_403_FORBIDDEN)
        
        # Filtros
        estado_pago = request.query_params.get("estado_pago")
        estado = request.query_params.get("estado")
        clinica_id = request.query_params.get("clinica_id")

        if user.ci:
            qs = Cita.objects.filter(paciente__ci=user.ci)
        else:
            qs = Cita.objects.filter(paciente__nombre__icontains=user.username)

        if estado_pago:
            qs = qs.filter(estado_pago=estado_pago)
        if estado:
            qs = qs.filter(estado=estado)
        if clinica_id:
            qs = qs.filter(psicologo__clinica_id=clinica_id)

        data = []
        for cita in qs.order_by("-fecha_hora"):
            psicologo_nombre = f"{cita.psicologo.first_name} {cita.psicologo.last_name}".strip() or cita.psicologo.username
            data.append({
                "id": cita.id,
                "fecha_hora": cita.fecha_hora.isoformat(),
                "motivo": cita.motivo,
                "estado": cita.estado,
                "estado_pago": cita.estado_pago,
                "monto": str(cita.monto),
                "psicologo_nombre": psicologo_nombre,
                "numero_ficha": cita.numero_ficha,
                "codigo_qr": cita.codigo_qr,
                "clinica_nombre": cita.psicologo.clinica.nombre if cita.psicologo.clinica else "General"
            })
        
        return Response({"citas": data}, status=status.HTTP_200_OK)

    def post(self, request):
        user = request.user
        if user.rol != 'PACIENTE':
            return Response({"detail": "Solo pacientes pueden crear citas móvil."}, status=status.HTTP_403_FORBIDDEN)

        psicologo_username = request.data.get("psicologo_username")
        try:
            psicologo = Usuario.objects.get(username=psicologo_username, rol='PSICOLOGO')
        except Usuario.DoesNotExist:
            return Response({"detail": "Especialista no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Buscar o crear Paciente en la clínica específica
        paciente, created = Paciente.objects.get_or_create(
            ci=user.ci if user.ci else user.username,
            clinica_id=psicologo.clinica_id,
            defaults={
                'nombre': f"{user.first_name} {user.last_name}".strip() or user.username,
                'telefono': user.telefono,
                'fecha_nacimiento': '2000-01-01',
            }
        )
        
        # Si recién se crea el paciente, le creamos su Historia Clínica vacía
        if created:
            from apps.P2_Gestion_Clinica.models import HistoriaClinica
            HistoriaClinica.objects.get_or_create(paciente=paciente)

        fecha_hora = request.data.get("fecha_hora")
        motivo = request.data.get("motivo", "")
        monto = request.data.get("monto", "120.00")

        cita = Cita.objects.create(
            paciente=paciente,
            psicologo=psicologo,
            fecha_hora=fecha_hora,
            motivo=motivo,
            estado='PENDIENTE',
            estado_pago='PENDIENTE',
            monto=monto
        )

        from django.utils.dateparse import parse_datetime
        fecha_obj = parse_datetime(fecha_hora)
        fecha_str = fecha_obj.strftime("%d/%m/%Y %H:%M") if fecha_obj else fecha_hora

        # Notificación al paciente
        NotificacionPush.objects.create(
            usuario=user,
            titulo="Cita Agendada",
            mensaje=f"Has agendado una cita con {psicologo.first_name} {psicologo.last_name} para el {fecha_str}."
        )
        
        # Notificación al psicólogo
        NotificacionPush.objects.create(
            usuario=psicologo,
            titulo="Nueva Cita Agendada",
            mensaje=f"El paciente {user.first_name} {user.last_name} ha agendado una cita contigo para el {fecha_str}."
        )

        # Notificación a la clínica
        if psicologo.clinica:
            admin_clinica = Usuario.objects.filter(clinica=psicologo.clinica, rol='ADMIN').first()
            if admin_clinica:
                NotificacionPush.objects.create(
                    usuario=admin_clinica,
                    titulo="Nueva Cita en Clínica",
                    mensaje=f"El paciente {user.first_name} {user.last_name} ha agendado una cita con {psicologo.first_name} para el {fecha_str}."
                )

        return Response({"id": cita.id, "mensaje": "Cita creada con éxito"}, status=status.HTTP_201_CREATED)

class MobileCitaCancelarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        user = request.user
        try:
            cita = Cita.objects.get(id=pk)
        except Cita.DoesNotExist:
            return Response({"detail": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        # Validaciones de Cancelación
        if cita.estado_pago == 'PAGADO':
            return Response({"detail": "No puede cancelar una cita que ya ha sido pagada."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. No se puede cancelar faltando menos de 1 hora
        tiempo_restante = cita.fecha_hora - timezone.now()
        if tiempo_restante.total_seconds() < 3600 and tiempo_restante.total_seconds() > 0:
            return Response({"detail": "No puede cancelar una cita faltando menos de 1 hora."}, status=status.HTTP_400_BAD_REQUEST)
        
        # 2. Control de 2 Strikes (máximo 2 cancelaciones por día)
        hoy = timezone.now().date()
        if user.ultima_cancelacion_fecha == hoy:
            if user.cancelaciones_hoy >= 2:
                return Response({"detail": "Has superado el límite de 2 cancelaciones diarias. Acceso restringido."}, status=status.HTTP_403_FORBIDDEN)
            user.cancelaciones_hoy += 1
        else:
            user.ultima_cancelacion_fecha = hoy
            user.cancelaciones_hoy = 1
        user.save()

        cita.estado = 'CANCELADA'
        cita.save()

        # Notificaciones
        psicologo = cita.psicologo
        clinica = psicologo.clinica
        fecha_str = cita.fecha_hora.strftime("%d/%m/%Y %H:%M")

        NotificacionPush.objects.create(
            usuario=user,
            titulo="Cita Cancelada",
            mensaje=f"Se canceló tu cita con {psicologo.first_name} {psicologo.last_name} en {clinica.nombre if clinica else 'Clínica'} para el {fecha_str}."
        )
        NotificacionPush.objects.create(
            usuario=psicologo,
            titulo="Cita Cancelada por Paciente",
            mensaje=f"El paciente {user.first_name} {user.last_name} canceló la cita del {fecha_str}."
        )
        if clinica:
            admin_clinica = Usuario.objects.filter(clinica=clinica, rol='ADMIN').first()
            if admin_clinica:
                NotificacionPush.objects.create(
                    usuario=admin_clinica,
                    titulo="Cita Cancelada en Clínica",
                    mensaje=f"El paciente {user.first_name} {user.last_name} canceló cita con {psicologo.first_name} el {fecha_str}."
                )

        return Response({"detail": "Cita cancelada exitosamente."}, status=status.HTTP_200_OK)

class MobileCitaFichaPDFAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, cita_id):
        try:
            from django.db.models import Q
            cita = Cita.objects.get(id=cita_id, paciente__ci=request.user.ci if request.user.ci else request.user.username)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        
        clinica_nombre = cita.psicologo.clinica.nombre if cita.psicologo.clinica else 'PsicoSystem'
        psicologo_nombre = f"{cita.psicologo.first_name} {cita.psicologo.last_name}".strip() or cita.psicologo.username
        paciente_nombre = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.username
        fecha_str = cita.fecha_hora.strftime('%d/%m/%Y %H:%M')

        c.setFont("Helvetica-Bold", 18)
        c.drawString(100, 750, "FICHA DE CITA MÉDICA - PsicoSystem")
        c.setFont("Helvetica", 12)
        c.drawString(100, 720, f"Clínica: {clinica_nombre}")
        c.drawString(100, 700, f"N° Ficha / Ticket: #{cita.id}")
        c.drawString(100, 680, f"Paciente: {paciente_nombre}")
        c.drawString(100, 660, f"Psicólogo: {psicologo_nombre}")
        c.drawString(100, 640, f"Fecha y Hora: {fecha_str}")
        c.drawString(100, 620, f"Monto: ${cita.monto}")
        c.showPage()
        c.save()

        pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Crear notificación en la base de datos
        NotificacionPush.objects.create(
            usuario=request.user,
            titulo="Ficha Médica Descargada",
            mensaje=f"Se descargó la ficha de tu cita en {clinica_nombre} con {psicologo_nombre} para el {fecha_str}."
        )

        return Response({"pdf_base64": pdf_base64, "mensaje": "Ficha generada correctamente"})

import decimal
import stripe
import json
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

stripe.api_key = getattr(settings, 'STRIPE_SECRET_KEY', '')

def _registrar_pago_exitoso(cita, user, metodo_pago):
    """Función compartida: marca la cita como PAGADA, crea transaccion y notificaciones."""
    cita.estado_pago = 'PAGADO'
    cita.save()

    psicologo = cita.psicologo
    monto = decimal.Decimal(str(cita.monto))
    fecha_str = cita.fecha_hora.strftime('%d/%m/%Y %H:%M')
    psicologo_nombre = f"{psicologo.first_name} {psicologo.last_name}".strip() or psicologo.username
    paciente_nombre = f"{user.first_name} {user.last_name}".strip() or user.username
    clinica_nombre = psicologo.clinica.nombre if psicologo.clinica else "la clínica"
    metodo_str = "QR" if metodo_pago == "QR" else "Tarjeta (Stripe)"

    # Actualizar saldo de la clínica
    if psicologo.clinica:
        try:
            saldo_actual = psicologo.clinica.saldo or decimal.Decimal('0.00')
            psicologo.clinica.saldo = saldo_actual + monto
            psicologo.clinica.save()
            TransaccionClinica.objects.create(
                clinica=psicologo.clinica,
                tipo='INGRESO_PACIENTE',
                monto=monto,
                descripcion=f"Pago cita #{cita.id} | Paciente: {paciente_nombre} | Método: {metodo_str}",
                metodo_pago=metodo_pago
            )
        except Exception:
            pass  # No bloquear el pago si hay error en la transacción interna

    # Notificación para el PACIENTE (estilo WhatsApp 🔔)
    NotificacionPush.objects.create(
        usuario=user,
        titulo=f"✅ Pago Exitoso — {metodo_str}",
        mensaje=(
            f"Tu pago de ${cita.monto} fue procesado con éxito.\n"
            f"📋 Motivo: {cita.motivo}\n"
            f"👨‍⚕️ Psicólogo: {psicologo_nombre}\n"
            f"🏥 Clínica: {clinica_nombre}\n"
            f"📅 Cita: {fecha_str}"
        )
    )

    # Notificación para el PSICÓLOGO
    NotificacionPush.objects.create(
        usuario=psicologo,
        titulo=f"💰 Pago Recibido — {metodo_str}",
        mensaje=(
            f"El paciente {paciente_nombre} pagó la cita de ${cita.monto}.\n"
            f"📋 Motivo: {cita.motivo}\n"
            f"📅 Fecha: {fecha_str}"
        )
    )

    # Notificación para el ADMIN de la clínica
    if psicologo.clinica:
        admin_clinica = Usuario.objects.filter(clinica=psicologo.clinica, rol='ADMIN').first()
        if admin_clinica:
            NotificacionPush.objects.create(
                usuario=admin_clinica,
                titulo=f"🏦 Ingreso Registrado — {metodo_str}",
                mensaje=(
                    f"Pago de ${cita.monto} recibido.\n"
                    f"👤 Paciente: {paciente_nombre}\n"
                    f"👨‍⚕️ Psicólogo: {psicologo_nombre}\n"
                    f"📋 Motivo: {cita.motivo}\n"
                    f"📅 Cita: {fecha_str}"
                )
            )


class MobilePacientePagarAPIView(APIView):
    """Endpoint para pago QR (simulado/confirmado por botón en app)."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cita_id = request.data.get("cita_id")

        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"detail": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        if cita.estado_pago == 'PAGADO':
            return Response({"detail": "Esta cita ya está pagada."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            _registrar_pago_exitoso(cita, user, "QR")
        except Exception as e:
            return Response({"detail": f"Error al registrar pago: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({
            "detail": "Pago QR procesado exitosamente.",
            "cita_id": cita.id,
            "estado_pago": "PAGADO"
        }, status=status.HTTP_201_CREATED)


class MobileStripeCheckoutAPIView(APIView):
    """Crea una Stripe Checkout Session y devuelve la URL de pago."""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cita_id = request.data.get("cita_id")

        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"detail": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        if cita.estado_pago == 'PAGADO':
            return Response({"detail": "Esta cita ya está pagada."}, status=status.HTTP_400_BAD_REQUEST)

        if not stripe.api_key or stripe.api_key == '':
            return Response({"detail": "Stripe no está configurado."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            psicologo_nombre = f"{cita.psicologo.first_name} {cita.psicologo.last_name}".strip() or cita.psicologo.username
            clinica_nombre = cita.psicologo.clinica.nombre if cita.psicologo.clinica else "PsicoSystem"
            monto_centavos = int(decimal.Decimal(str(cita.monto)) * 100)
            
            # URL de retorno - la app manejará el deep link
            frontend_url = getattr(settings, 'FRONTEND_URL', 'https://psicosystem-frontend-21h1.onrender.com')
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Consulta Psicológica — {cita.motivo or "Cita"}',
                            'description': f'Psicólogo: {psicologo_nombre} | Clínica: {clinica_nombre}',
                        },
                        'unit_amount': monto_centavos,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{frontend_url}/pago-exitoso/?cita_id={cita.id}&session_id={{CHECKOUT_SESSION_ID}}',
                cancel_url=f'{frontend_url}/pago-cancelado/?cita_id={cita.id}',
                metadata={
                    'cita_id': str(cita.id),
                    'user_id': str(user.id),
                    'metodo_pago': 'TARJETA_STRIPE',
                }
            )
            
            return Response({
                "checkout_url": session.url,
                "session_id": session.id,
                "cita_id": cita.id
            }, status=status.HTTP_200_OK)
            
        except stripe.error.StripeError as e:
            return Response({"detail": f"Error de Stripe: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"detail": f"Error interno: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@method_decorator(csrf_exempt, name='dispatch')
class MobileStripeWebhookAPIView(APIView):
    """Webhook de Stripe para confirmar pago y marcar cita como PAGADA."""
    permission_classes = []
    authentication_classes = []

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE', '')
        webhook_secret = getattr(settings, 'STRIPE_WEBHOOK_SECRET', '')

        try:
            if webhook_secret:
                event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
            else:
                event = stripe.Event.construct_from(json.loads(payload), stripe.api_key)
        except (ValueError, stripe.error.SignatureVerificationError) as e:
            return HttpResponse(status=400)

        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            cita_id = session.get('metadata', {}).get('cita_id')
            user_id = session.get('metadata', {}).get('user_id')

            if cita_id and user_id:
                try:
                    cita = Cita.objects.get(id=int(cita_id), estado_pago='PENDIENTE')
                    user = Usuario.objects.get(id=int(user_id))
                    _registrar_pago_exitoso(cita, user, "TARJETA_STRIPE")
                except (Cita.DoesNotExist, Usuario.DoesNotExist):
                    pass

        return HttpResponse(status=200)



class MobileCitasDisponibilidadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        psicologo_username = request.query_params.get("psicologo_username")
        fecha = request.query_params.get("fecha")
        
        if not psicologo_username or not fecha:
            return Response({"detail": "psicologo_username y fecha son requeridos."}, status=status.HTTP_400_BAD_REQUEST)

        citas_psicologo = Cita.objects.filter(
            psicologo__username=psicologo_username,
            fecha_hora__date=fecha,
            estado__in=['PENDIENTE', 'CONFIRMADA', 'REALIZADA']
        )
        
        user = request.user
        citas_paciente = Cita.objects.filter(
            paciente__ci=user.ci if user.ci else user.username,
            fecha_hora__date=fecha,
            estado__in=['PENDIENTE', 'CONFIRMADA', 'REALIZADA']
        )

        horas_ocupadas = set()
        for c in citas_psicologo:
            # Convirtiendo datetime local a la hora de la cita
            local_dt = timezone.localtime(c.fecha_hora)
            horas_ocupadas.add(local_dt.strftime("%H:%M"))
        for c in citas_paciente:
            local_dt = timezone.localtime(c.fecha_hora)
            horas_ocupadas.add(local_dt.strftime("%H:%M"))

        return Response({"horas_ocupadas": list(horas_ocupadas)}, status=status.HTTP_200_OK)


class MobilePsicologosListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        psicologos = Usuario.objects.filter(rol='PSICOLOGO', is_active=True)
        data = []
        for p in psicologos:
            data.append({
                "id": p.id,
                "first_name": p.first_name,
                "last_name": p.last_name,
                "username": p.username,
                "especialidad": getattr(p, 'especialidad', 'Psicólogo General'),
                "clinica": p.clinica.nombre if p.clinica else "Sin Clínica Asignada"
            })
        return Response(data, status=status.HTTP_200_OK)


class MobileRecomendacionesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.rol != 'PACIENTE':
            return Response({"detail": "Solo pacientes pueden ver sus recomendaciones."}, status=status.HTTP_403_FORBIDDEN)
        
        from apps.P2_Gestion_Clinica.models import Recomendacion
        
        ci_a_buscar = user.ci if user.ci else user.username
        qs = Recomendacion.objects.filter(paciente__ci=ci_a_buscar).order_by('-fecha_creacion')
        
        data = []
        for r in qs:
            data.append({
                "id": r.id,
                "texto": r.texto,
                "estado": r.estado,
                "fecha_creacion": r.fecha_creacion.isoformat(),
                "fecha_sesion": r.evolucion.fecha_sesion.isoformat() if r.evolucion.fecha_sesion else None,
                "psicologo_nombre": f"{r.psicologo.first_name} {r.psicologo.last_name}".strip() or r.psicologo.username,
                "clinica_nombre": r.psicologo.clinica.nombre if getattr(r.psicologo, 'clinica', None) else "Clínica General"
            })
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        user = request.user
        if user.rol != 'PACIENTE':
            return Response({"detail": "Solo pacientes pueden actualizar sus recomendaciones."}, status=status.HTTP_403_FORBIDDEN)
        
        from apps.P2_Gestion_Clinica.models import Recomendacion
        try:
            ci_a_buscar = user.ci if user.ci else user.username
            recomendacion = Recomendacion.objects.get(pk=pk, paciente__ci=ci_a_buscar)
        except Recomendacion.DoesNotExist:
            return Response({"detail": "Recomendación no encontrada."}, status=status.HTTP_404_NOT_FOUND)
        
        nuevo_estado = request.data.get('estado')
        if nuevo_estado in ['PENDIENTE', 'EN_PROGRESO', 'COMPLETADO']:
            recomendacion.estado = nuevo_estado
            recomendacion.save()
            return Response({"detail": "Estado actualizado correctamente.", "estado": recomendacion.estado}, status=status.HTTP_200_OK)
        return Response({"detail": "Estado no válido."}, status=status.HTTP_400_BAD_REQUEST)
