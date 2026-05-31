from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.P1_Identidad_Acceso.permissions import (
    HasClinicaAsignada,
    EsPsicologoOAdministrador,
)
from apps.P4_IA_Administracion.models import LogAuditoria

from .forms import CitaForm
from .models import Cita
from .serializers import CitaSerializer


@login_required
def registrar_cita_view(request):
    if not getattr(request.user, "clinica", None):
        messages.error(
            request,
            "Tu cuenta no está asignada a ninguna clínica. No puedes registrar citas.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = CitaForm(request.POST, user=request.user)
        if form.is_valid():
            cita = form.save()
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Registró una nueva cita: {cita.paciente} — {cita.fecha_hora}",
            )
            return redirect("listar_citas")
    else:
        form = CitaForm(user=request.user)

    return render(request, "P3_Logistica_Citas/registrar_cita.html", {"form": form})


@login_required
def editar_cita_view(request, pk):
    cita = get_object_or_404(
        Cita, pk=pk, paciente__clinica=request.user.clinica
    )
    if request.method == "POST":
        form = CitaForm(request.POST, instance=cita, user=request.user)
        if form.is_valid():
            cita = form.save()
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Actualizó cita: {cita.paciente} — {cita.fecha_hora}",
            )
            return redirect("listar_citas")
    else:
        form = CitaForm(instance=cita, user=request.user)
    return render(
        request,
        "P3_Logistica_Citas/editar_cita.html",
        {"form": form, "cita": cita},
    )


@login_required
def listar_citas_view(request):
    citas = Cita.objects.filter(clinica=request.user.clinica).select_related(
        "paciente", "psicologo"
    ).order_by("fecha_hora")
    return render(request, "P3_Logistica_Citas/cita_list.html", {"citas": citas})


class CitaListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = CitaSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return (
            Cita.objects.filter(clinica=self.request.user.clinica)
            .select_related("paciente", "psicologo")
            .order_by("fecha_hora")
        )

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        cita = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Programó cita (API): {cita.paciente} — {cita.fecha_hora}",
        )


class CitaRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = CitaSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return Cita.objects.filter(
            clinica=self.request.user.clinica
        ).select_related("paciente", "psicologo")

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_update(self, serializer):
        cita = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Actualizó cita (API): id={cita.pk}",
        )

# ==============================================================================
# T029/T030/T032: Motor de Citas y Control de Asistencia
# ==============================================================================
from rest_framework import viewsets
from rest_framework.decorators import action
from django.core.mail import send_mail
from django.conf import settings
from .models import ListaEspera
from .serializers import ListaEsperaSerializer

class CitaViewSet(viewsets.ModelViewSet):
    serializer_class = CitaSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get_queryset(self):
        return Cita.objects.filter(clinica=self.request.user.clinica)

    def perform_create(self, serializer):
        cita = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Programó cita (ViewSet): {cita.paciente} — {cita.fecha_hora}",
        )
        
        # Notificación por Email
        mensaje = f"Se ha programado una nueva cita para {cita.paciente.nombre} el {cita.fecha_hora.strftime('%d/%m/%Y a las %H:%M')} con el profesional {cita.psicologo.get_full_name()}."
        send_mail(
            subject='Nueva Cita Programada - PsicoSystem',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[self.request.user.email or 'admin@psicosystem.com'],
            fail_silently=True,
        )

    @action(detail=True, methods=['post'])
    def enviar_recordatorio(self, request, pk=None):
        """CU26: Enviar recordatorio de cita al paciente."""
        cita = self.get_object()
        paciente = cita.paciente
        
        # Simulación de envío de recordatorio (Email/SMS)
        mensaje = f"Recordatorio: Tienes una cita con el psicólogo {cita.psicologo.get_full_name()} el {cita.fecha_hora.strftime('%d/%m/%Y a las %H:%M')}."
        
        try:
            # En entorno local esto imprimirá en la consola por la config de EMAIL_BACKEND
            send_mail(
                subject='Recordatorio de Cita - PsicoSystem',
                message=mensaje,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[request.user.email or 'paciente@ejemplo.com'],
                fail_silently=False,
            )
            
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Envió recordatorio de cita a {paciente.nombre}"
            )
            return Response({"status": "Recordatorio enviado correctamente."})
        except Exception as e:
            return Response({"error": f"No se pudo enviar el recordatorio: {str(e)}"}, status=500)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """CU15: Cancelar cita con notificación automática."""
        cita = self.get_object()
        cita.estado = 'CANCELADA'
        cita.save()
        
        # Notificación automática (CU26)
        mensaje = f"Su cita programada para el {cita.fecha_hora.strftime('%d/%m/%Y')} ha sido CANCELADA."
        
        from apps.P1_Identidad_Acceso.models import Usuario, NotificacionPush
        paciente_user = Usuario.objects.filter(ci=cita.paciente.ci).first()
        if paciente_user:
            NotificacionPush.objects.create(
                usuario=paciente_user,
                titulo="❌ Cita Cancelada por Clínica",
                mensaje=f"Tu cita en la clínica ha sido cancelada. {mensaje}"
            )

        send_mail(
            subject='Notificación de Cancelación - PsicoSystem',
            message=mensaje,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[request.user.email or 'paciente@ejemplo.com'],
            fail_silently=True,
        )

        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Canceló cita de {cita.paciente.nombre} (ID={cita.pk})"
        )
        return Response({"status": "Cita cancelada y paciente notificado."})

class ListaEsperaViewSet(viewsets.ModelViewSet):
    serializer_class = ListaEsperaSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get_queryset(self):
        return ListaEspera.objects.filter(clinica=self.request.user.clinica)

from django.utils.dateparse import parse_date
from django.utils import timezone
from rest_framework.views import APIView

class MobileCitasDisponibilidadAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        psicologo_username = request.query_params.get('psicologo_username')
        fecha_str = request.query_params.get('fecha')
        
        if not psicologo_username or not fecha_str:
            return Response({"error": "Faltan parámetros."}, status=400)
            
        fecha = parse_date(fecha_str)
        if not fecha:
            return Response({"error": "Formato de fecha inválido."}, status=400)
            
        citas = Cita.objects.filter(
            psicologo__username=psicologo_username,
            fecha_hora__date=fecha,
            estado__in=['PROGRAMADA', 'CONFIRMADA']
        )
        
        # Devolver las horas ocupadas en formato HH:MM
        horas_ocupadas = [timezone.localtime(c.fecha_hora).strftime('%H:%M') for c in citas]
        return Response({"horas_ocupadas": horas_ocupadas})


class MobileCitasAPIView(APIView):
    """
    [CU-MOBILE]
    GET : Historial de citas del paciente autenticado.
    POST: Crear una cita desde la App Móvil.
    El paciente se identifica automáticamente por el CI vinculado a su cuenta de usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Devuelve el historial de citas del paciente autenticado."""
        from apps.P2_Gestion_Clinica.models import Paciente
        from django.utils import timezone as tz

        user = request.user
        ci_del_usuario = user.ci

        if not ci_del_usuario:
            return Response(
                {"citas": [], "total": 0, "advertencia": "Tu cuenta no tiene CI registrado."},
                status=200,
            )

        try:
            paciente = Paciente.objects.get(ci=ci_del_usuario)
        except Paciente.DoesNotExist:
            return Response(
                {"citas": [], "total": 0, "advertencia": "No se encontró tu expediente de paciente."},
                status=200,
            )

        estado = request.query_params.get('estado')
        estado_pago = request.query_params.get('estado_pago')
        clinica_id = request.query_params.get('clinica_id')
        historial_completo = request.query_params.get('historial_completo')

        qs = Cita.objects.filter(paciente=paciente).select_related('psicologo', 'clinica', 'paciente__clinica').order_by('-fecha_hora')
        if estado:
            qs = qs.filter(estado=estado)
        elif not historial_completo:
            qs = qs.exclude(estado='CANCELADA')
        if estado_pago:
            qs = qs.filter(estado_pago=estado_pago)
        if clinica_id:
            qs = qs.filter(clinica_id=clinica_id)

        citas_data = []
        for cita in qs:
            citas_data.append({
                "id": cita.pk,
                "fecha_hora": cita.fecha_hora.isoformat(),
                "motivo": cita.motivo,
                "estado": cita.estado,
                "estado_pago": cita.estado_pago,
                "monto": str(cita.monto),
                "psicologo_nombre": cita.psicologo.get_full_name() or cita.psicologo.username,
                "psicologo_username": cita.psicologo.username,
                "clinica_nombre": cita.clinica.nombre if cita.clinica else (cita.paciente.clinica.nombre if cita.paciente.clinica else 'Sin Clínica'),
                "numero_ficha": cita.numero_ficha or f"FICHA-{cita.pk:05d}",
                "codigo_qr": cita.codigo_qr or f"QR-CITA-{cita.pk}",
            })

        return Response({"citas": citas_data, "total": len(citas_data)}, status=200)

    def post(self, request):
        from apps.P2_Gestion_Clinica.models import Paciente
        from apps.P1_Identidad_Acceso.models import Clinica
        from django.utils.dateparse import parse_datetime

        user = request.user
        fecha_hora_str = request.data.get('fecha_hora')
        motivo = request.data.get('motivo', '')
        psicologo_username = request.data.get('psicologo_username')
        clinica_id = request.data.get('clinica_id')
        monto = request.data.get('monto', 120.00)

        # Validaciones básicas
        if not all([fecha_hora_str, psicologo_username, clinica_id]):
            return Response(
                {"error": "Faltan campos requeridos: fecha_hora, psicologo_username, clinica_id."},
                status=400
            )

        # Buscar psicólogo
        try:
            from apps.P1_Identidad_Acceso.models import Usuario
            psicologo = Usuario.objects.get(username=psicologo_username, rol='PSICOLOGO')
        except Usuario.DoesNotExist:
            return Response({"error": "El psicólogo no fue encontrado."}, status=404)

        # Parsear fecha
        fecha_hora = parse_datetime(fecha_hora_str)
        if not fecha_hora:
            return Response({"error": "Formato de fecha inválido. Usa ISO 8601."}, status=400)

        # Localizar si viene sin timezone
        from django.utils import timezone as tz
        if fecha_hora.tzinfo is None:
            from django.utils.timezone import make_aware
            fecha_hora = make_aware(fecha_hora)

        # Buscar el objeto Paciente por el CI del usuario autenticado
        ci_del_usuario = user.ci
        if not ci_del_usuario:
            return Response(
                {"error": "Tu cuenta no tiene CI registrado. Actualiza tu perfil."},
                status=400
            )

        try:
            paciente = Paciente.objects.get(ci=ci_del_usuario)
        except Paciente.DoesNotExist:
            return Response(
                {"error": "No se encontró tu expediente de paciente. Contacta con la clínica."},
                status=404
            )

        # Validación de horario cruzado
        cruce_existente = Cita.objects.filter(
            paciente=paciente,
            fecha_hora=fecha_hora,
            estado__in=['PENDIENTE', 'PROGRAMADA', 'CONFIRMADA']
        ).exists()

        if cruce_existente:
            return Response(
                {"error": "Usted ya cuenta con una cita programada en este horario en otra clínica."},
                status=400
            )

        # Crear la cita
        try:
            cita = Cita.objects.create(
                paciente=paciente,
                psicologo=psicologo,
                clinica_id=clinica_id,
                fecha_hora=fecha_hora,
                motivo=motivo,
                estado='PENDIENTE',
                estado_pago='PENDIENTE',
                monto=monto,
            )
            
            # Generar ficha y qr
            cita.numero_ficha = f"FICHA-{cita.pk:05d}"
            cita.codigo_qr = f"PAGO_CITA_{cita.pk}_{cita.monto}"
            cita.save(update_fields=['numero_ficha', 'codigo_qr'])
            
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        # Actualizar la clínica del paciente si no tiene una asignada
        if paciente.clinica_id is None:
            paciente.clinica_id = clinica_id
            paciente.save(update_fields=['clinica_id'])

        # ── Notificación in-app: aparece en la campanita del paciente ──
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        from django.utils import timezone as tz_now

        fecha_local = tz_now.localtime(cita.fecha_hora)
        clinica = Clinica.objects.filter(id=clinica_id).first()
        clinica_nombre = clinica.nombre if clinica else 'la clínica'
        NotificacionPush.objects.create(
            usuario=user,
            titulo="✅ Cita Programada",
            mensaje=(
                f"Tu cita en {clinica_nombre} "
                f"con el/la Dr(a). {psicologo.get_full_name() or psicologo.username} "
                f"fue agendada para el {fecha_local.strftime('%d/%m/%Y a las %H:%M')}. "
                f"Motivo: {motivo or 'Sin especificar'}."
            ),
        )

        # ── Notificación a la Web (Clínica y Psicólogo) ──
        # Notificar a los administradores de la clínica
        admins = Usuario.objects.filter(rol='ADMIN', clinica_id=clinica_id)
        for admin in admins:
            NotificacionPush.objects.create(
                usuario=admin,
                titulo="📅 Nueva Cita (App)",
                mensaje=f"El paciente {paciente.nombre} (CI: {paciente.ci}) agendó una cita con {psicologo.get_full_name()} para el {fecha_local.strftime('%d/%m/%Y a las %H:%M')}."
            )
            
        # Notificar al psicólogo
        NotificacionPush.objects.create(
            usuario=psicologo,
            titulo="📅 Tienes una nueva cita",
            mensaje=f"Paciente: {paciente.nombre}. Fecha: {fecha_local.strftime('%d/%m/%Y a las %H:%M')}."
        )

        return Response({
            "id": cita.pk,
            "mensaje": "Cita programada exitosamente.",
            "fecha_hora": cita.fecha_hora.isoformat(),
            "psicologo": psicologo.get_full_name() or psicologo.username,
            "estado": cita.estado,
        }, status=201)


class MobileCitaCancelarAPIView(APIView):
    """
    [CU-MOBILE] POST: Cancelar una cita desde la App Móvil.
    Reglas: no se puede cancelar faltando menos de 1 hora y máx. 2 cancelaciones/día.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        from apps.P2_Gestion_Clinica.models import Paciente
        from django.utils import timezone as tz
        from django.db import models as db_models

        user = request.user

        # Verificar que la cita pertenece al paciente autenticado
        try:
            paciente = Paciente.objects.get(ci=user.ci)
        except Paciente.DoesNotExist:
            return Response({"error": "No se encontró tu expediente de paciente."}, status=404)

        try:
            cita = Cita.objects.get(pk=pk, paciente=paciente)
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada o no te pertenece."}, status=404)

        if cita.estado in ('CANCELADA', 'REALIZADA'):
            return Response({"error": f"La cita ya está en estado '{cita.estado}' y no puede cancelarse."}, status=400)
            
        if cita.estado_pago == 'PAGADO':
            return Response({"error": "No puedes cancelar una cita que ya ha sido pagada."}, status=400)

        # Regla 1: No cancelar faltando menos de 1 hora
        ahora = tz.now()
        tiempo_restante = cita.fecha_hora - ahora
        if tiempo_restante.total_seconds() < 3600:
            return Response(
                {"error": "No puedes cancelar citas con menos de 1 hora de antelación."},
                status=400,
            )

        # Regla 2: Máx. 2 cancelaciones por día
        hoy = ahora.date()
        if user.ultima_cancelacion_fecha == hoy:
            if user.cancelaciones_hoy >= 2:
                return Response(
                    {"error": "Has alcanzado el límite de 2 cancelaciones diarias."},
                    status=400,
                )
            user.cancelaciones_hoy += 1
        else:
            user.cancelaciones_hoy = 1
            user.ultima_cancelacion_fecha = hoy
        user.save(update_fields=['cancelaciones_hoy', 'ultima_cancelacion_fecha'])

        # Cancelar la cita
        cita.estado = 'CANCELADA'
        cita.save(update_fields=['estado'])

        # Notificación in-app al paciente
        fecha_local = tz.localtime(cita.fecha_hora)
        motivo_str = request.data.get('motivo', 'Cancelación por el paciente')
        NotificacionPush.objects.create(
            usuario=user,
            titulo="❌ Cita Cancelada",
            mensaje=(
                f"Tu cita en {cita.clinica.nombre if cita.clinica else 'la clínica'} "
                f"con el/la Dr(a). {cita.psicologo.get_full_name() or cita.psicologo.username} "
                f"del {fecha_local.strftime('%d/%m/%Y a las %H:%M')} ha sido cancelada.\n"
                f"Motivo: {motivo_str}"
            ),
        )

        # ── Notificación a la Web (Clínica) ──
        if cita.clinica_id:
            admins = db_models.apps.get_model('P1_Identidad_Acceso', 'Usuario').objects.filter(rol='ADMIN', clinica_id=cita.clinica_id)
            for admin in admins:
                NotificacionPush.objects.create(
                    usuario=admin,
                    titulo="❌ Cita Cancelada",
                    mensaje=f"El paciente {paciente.nombre} ha cancelado su cita del {fecha_local.strftime('%d/%m/%Y a las %H:%M')}."
                )

        # Notificar al psicólogo
        NotificacionPush.objects.create(
            usuario=cita.psicologo,
            titulo="❌ Cita Cancelada",
            mensaje=f"La cita con el paciente {paciente.nombre} programada para el {fecha_local.strftime('%d/%m/%Y a las %H:%M')} ha sido cancelada."
        )

        return Response({"mensaje": "Cita cancelada exitosamente.", "estado": cita.estado}, status=200)

class CreateStripePaymentIntentView(APIView):
    """
    [CU-MOBILE] POST: Crea un PaymentIntent de Stripe para cobrar una cita.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import stripe
        from django.conf import settings
        from apps.P2_Gestion_Clinica.models import Paciente
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = request.user
        cita_id = request.data.get('cita_id')
        
        try:
            paciente = Paciente.objects.get(ci=user.ci)
            cita = Cita.objects.get(pk=cita_id, paciente=paciente)
        except (Paciente.DoesNotExist, Cita.DoesNotExist):
            return Response({"error": "Cita no encontrada."}, status=404)

        if cita.estado_pago == 'PAGADO':
            return Response({"error": "Esta cita ya está pagada."}, status=400)

        # Crear el PaymentIntent en Stripe
        try:
            monto_centavos = int(float(cita.monto) * 100)
            if monto_centavos <= 0:
                monto_centavos = 12000 # Fallback 120.00 si no hay monto

            intent = stripe.PaymentIntent.create(
                amount=monto_centavos,
                currency='usd',
                metadata={'cita_id': cita.id, 'paciente_ci': paciente.ci},
                automatic_payment_methods={'enabled': True},
            )
            return Response({
                'client_secret': intent.client_secret,
                'payment_intent_id': intent.id
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class MobileStripeCheckoutSessionView(APIView):
    """
    [CU-MOBILE] POST: Crea una Stripe Checkout Session y devuelve la URL para redirigir al navegador.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import stripe
        from django.conf import settings
        from apps.P2_Gestion_Clinica.models import Paciente
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        user = request.user
        cita_id = request.data.get('cita_id')
        
        try:
            paciente = Paciente.objects.get(ci=user.ci)
            cita = Cita.objects.get(pk=cita_id, paciente=paciente)
        except (Paciente.DoesNotExist, Cita.DoesNotExist):
            return Response({"error": "Cita no encontrada."}, status=404)

        if cita.estado_pago == 'PAGADO':
            return Response({"error": "Esta cita ya está pagada."}, status=400)

        try:
            monto_centavos = int(float(cita.monto) * 100)
            if monto_centavos <= 0:
                monto_centavos = 12000

            domain_url = "https://psicosystem-backend.onrender.com"
            success_url = f"{domain_url}/api/mobile/stripe/checkout-success/?session_id={{CHECKOUT_SESSION_ID}}&cita_id={cita.id}"

            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'Pago de Cita Psicológica - {paciente.nombre}',
                            'description': cita.motivo,
                        },
                        'unit_amount': monto_centavos,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=success_url,
                cancel_url="https://psicosystem-backend.onrender.com/", 
                metadata={'cita_id': cita.id, 'paciente_ci': paciente.ci},
            )
            return Response({
                'checkout_url': session.url,
            })
        except Exception as e:
            return Response({"error": str(e)}, status=500)


class MobileStripeCheckoutSuccessView(APIView):
    """
    [CU-MOBILE] GET: Endpoint al que Stripe redirige cuando el pago en el Checkout fue exitoso.
    """
    permission_classes = [] 

    def get(self, request):
        import stripe
        from django.conf import settings
        from django.http import HttpResponse
        from apps.P1_Identidad_Acceso.models import Transaccion

        stripe.api_key = settings.STRIPE_SECRET_KEY
        session_id = request.GET.get('session_id')
        cita_id = request.GET.get('cita_id')

        if not session_id or not cita_id:
            return HttpResponse("Faltan parámetros", status=400)

        try:
            session = stripe.checkout.Session.retrieve(session_id)
            if session.payment_status == 'paid':
                cita = Cita.objects.get(pk=cita_id)
                cita.estado_pago = 'PAGADO'
                cita.estado = 'CONFIRMADA'
                cita.save()

                if not hasattr(cita, 'transaccion'):
                    Transaccion.objects.create(
                        clinica=cita.paciente.clinica,
                        monto=cita.monto,
                        concepto=f"Pago de cita (Stripe Checkout) - {cita.motivo}",
                        tipo='INGRESO',
                        metodo_pago='STRIPE'
                    )
                else:
                    t = cita.transaccion
                    t.metodo_pago = 'STRIPE'
                    t.save()
                
                html = f"""
                <html>
                <head>
                    <meta name="viewport" content="width=device-width, initial-scale=1">
                    <script>
                        setTimeout(function() {{
                            window.location.href = "intent://pago-exitoso#Intent;scheme=psicosystem;package=com.example.psicosystem_mobile;end";
                        }}, 2000);
                    </script>
                    <style>
                        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f0fdf4; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }}
                        .card {{ background: white; padding: 40px 20px; border-radius: 16px; box-shadow: 0 10px 15px -3px rgba(0,0,0,0.1); text-align: center; max-width: 400px; width: 90%; }}
                        .icon {{ color: #16a34a; font-size: 60px; margin-bottom: 20px; }}
                        h1 {{ color: #16a34a; margin-top: 0; font-size: 24px; }}
                        p {{ color: #475569; font-size: 16px; line-height: 1.5; }}
                        .btn {{ display: inline-block; margin-top: 20px; padding: 12px 24px; background-color: #16a34a; color: white; text-decoration: none; border-radius: 8px; font-weight: bold; }}
                    </style>
                </head>
                <body>
                    <div class="card">
                        <div class="icon">✓</div>
                        <h1>Pago Exitoso</h1>
                        <p>Tu cita ha sido confirmada y pagada correctamente por un monto de ${cita.monto}.</p>
                        <p>Serás redirigido automáticamente a la aplicación en un par de segundos...</p>
                        <a href="intent://pago-exitoso#Intent;scheme=psicosystem;package=com.example.psicosystem_mobile;end" class="btn">Volver a PsicoSystem</a>
                    </div>
                </body>
                </html>
                """
                return HttpResponse(html)
            else:
                return HttpResponse("El pago no está completado en Stripe.", status=400)
        except Exception as e:
            return HttpResponse(f"Error procesando el pago: {str(e)}", status=500)


class MobileCitaPagarAPIView(APIView):
    """
    [CU-MOBILE] POST: Confirma el pago de una cita desde la App Móvil (vía Stripe o QR).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        import stripe
        from django.conf import settings
        from apps.P2_Gestion_Clinica.models import Paciente
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        user = request.user
        cita_id = request.data.get('cita_id')
        metodo_pago = request.data.get('metodo_pago', 'QR')
        payment_intent_id = request.data.get('payment_intent_id')
        
        try:
            paciente = Paciente.objects.get(ci=user.ci)
            cita = Cita.objects.get(pk=cita_id, paciente=paciente)
        except (Paciente.DoesNotExist, Cita.DoesNotExist):
            return Response({"error": "Cita no encontrada o no te pertenece."}, status=404)

        if cita.estado_pago == 'PAGADO':
            return Response({"error": "Esta cita ya está pagada."}, status=400)

        # Verificación con Stripe si el método es TARJETA
        if metodo_pago == 'TARJETA':
            if not payment_intent_id:
                return Response({"error": "No se proporcionó el payment_intent_id."}, status=400)
            try:
                intent = stripe.PaymentIntent.retrieve(payment_intent_id)
                if intent.status != 'succeeded':
                    return Response({"error": f"El pago en Stripe no fue completado. Estado: {intent.status}"}, status=400)
            except Exception as e:
                return Response({"error": f"Error al verificar Stripe: {str(e)}"}, status=500)

        # Resto del proceso (marcar pagado, contabilidad, notificaciones)
        cita.estado_pago = 'PAGADO'
        if cita.estado == 'PENDIENTE':
            cita.estado = 'PROGRAMADA'
        cita.save(update_fields=['estado_pago', 'estado'])

        # --- Crear Transaccion y Comprobante (Para que aparezca en el Dashboard Web) ---
        from apps.P4_IA_Administracion.models import Transaccion, Comprobante
        import uuid
        try:
            transaccion = Transaccion.objects.create(
                clinica_id=cita.clinica_id or paciente.clinica_id,
                paciente=paciente,
                monto=cita.monto,
                concepto=f"Pago por cita {cita.numero_ficha or cita.pk}",
                metodo_pago='STRIPE' if metodo_pago == 'TARJETA' else 'QR'
            )
            Comprobante.objects.create(
                transaccion=transaccion,
                nro_comprobante=f"REC-{uuid.uuid4().hex[:8].upper()}"
            )
        except Exception as e:
            pass # Ignorar fallas contables si ya se marcó la cita como pagada

        clinica_nombre = cita.clinica.nombre if cita.clinica else 'la clínica'
        metodo_str = 'Tarjeta (Stripe)' if metodo_pago == 'TARJETA' else 'QR'
        mensaje_notif = f"Tu pago de ${cita.monto} mediante {metodo_str} para la cita con {cita.psicologo.get_full_name()} en {clinica_nombre} ha sido procesado correctamente."
        
        # Notificación
        NotificacionPush.objects.create(
            usuario=user,
            titulo="✅ Pago Exitoso",
            mensaje=mensaje_notif,
        )

        # ── Notificación a la Web (Clínica) ──
        from apps.P1_Identidad_Acceso.models import Usuario
        if cita.clinica_id:
            admins = Usuario.objects.filter(rol='ADMIN', clinica_id=cita.clinica_id)
            for admin in admins:
                NotificacionPush.objects.create(
                    usuario=admin,
                    titulo="💰 Pago Recibido",
                    mensaje=f"Se recibió un pago de ${cita.monto} mediante {metodo_str} del paciente {paciente.nombre} en {clinica_nombre}."
                )

        return Response({
            "mensaje": "Pago exitoso", 
            "estado_pago": cita.estado_pago, 
            "estado": cita.estado,
            "notificacion_titulo": "✅ Pago Exitoso",
            "notificacion_mensaje": mensaje_notif
        }, status=201)

import io
from django.http import HttpResponse

class MobileCitaComprobantePDFAPIView(APIView):
    """
    [CU-MOBILE] GET: Genera un comprobante PDF para la cita.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        from apps.P2_Gestion_Clinica.models import Paciente
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import letter
        from reportlab.lib import colors
        from django.utils import timezone as tz

        user = request.user
        try:
            cita = Cita.objects.get(pk=pk)
            if cita.paciente.ci != user.ci:
                return Response({"error": "Cita no te pertenece."}, status=403)
            paciente = cita.paciente
        except Cita.DoesNotExist:
            return Response({"error": "Cita no encontrada."}, status=404)

        buffer = io.BytesIO()
        c = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        # Header
        c.setFillColor(colors.HexColor("#2563EB"))
        c.rect(0, height - 80, width, 80, fill=1, stroke=0)
        c.setFillColor(colors.white)
        c.setFont("Helvetica-Bold", 24)
        c.drawString(40, height - 50, "Comprobante de Cita - PsicoSystem")

        # Info
        c.setFillColor(colors.black)
        c.setFont("Helvetica", 12)
        y = height - 120

        # Datos de la clínica
        clinica_nombre = cita.clinica.nombre if cita.clinica else (cita.paciente.clinica.nombre if cita.paciente.clinica else 'Clínica Desconocida')
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Datos de la Clínica")
        c.setFont("Helvetica", 12)
        y -= 20
        c.drawString(40, y, f"Nombre: {clinica_nombre}")

        # Datos del Paciente
        y -= 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Datos del Paciente")
        c.setFont("Helvetica", 12)
        y -= 20
        c.drawString(40, y, f"Nombre: {paciente.nombre}")
        y -= 20
        c.drawString(40, y, f"CI: {paciente.ci}")

        # Datos de la Cita
        y -= 40
        c.setFont("Helvetica-Bold", 14)
        c.drawString(40, y, "Datos de la Cita")
        c.setFont("Helvetica", 12)
        y -= 20
        fecha_local = tz.localtime(cita.fecha_hora)
        c.drawString(40, y, f"Fecha y Hora: {fecha_local.strftime('%d/%m/%Y a las %H:%M')}")
        y -= 20
        psicologo_nombre = cita.psicologo.get_full_name() or cita.psicologo.username
        c.drawString(40, y, f"Especialista: Dr(a). {psicologo_nombre}")
        y -= 20
        c.drawString(40, y, f"Número de Ficha: {cita.numero_ficha or f'FICHA-{cita.pk:05d}'}")
        y -= 20
        c.drawString(40, y, f"Estado: {cita.estado}")
        y -= 20
        c.drawString(40, y, f"Motivo: {cita.motivo or 'Sin especificar'}")

        # QR Text (Simulado como texto si no se tiene librería para dibujar QR en ReportLab)
        y -= 60
        c.setFont("Helvetica-Bold", 12)
        c.drawString(40, y, "Código QR de Verificación:")
        c.setFont("Helvetica", 10)
        y -= 20
        c.drawString(40, y, cita.codigo_qr or f"PAGO_CITA_{cita.pk}_{cita.monto}")

        # Footer
        c.setFont("Helvetica-Oblique", 10)
        c.setFillColor(colors.gray)
        c.drawString(40, 40, "Este documento es válido como comprobante de reserva en PsicoSystem.")

        c.showPage()
        c.save()
        buffer.seek(0)
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="Comprobante_Cita_{cita.numero_ficha}.pdf"'
        return response
