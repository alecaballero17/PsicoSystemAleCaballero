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
        
        try:
            paciente = Paciente.objects.get(ci=user.ci) if user.ci else Paciente.objects.filter(nombre__icontains=user.username).first()
            if not paciente:
                return Response({"detail": "Perfil de paciente no encontrado."}, status=status.HTTP_404_NOT_FOUND)
        except Paciente.DoesNotExist:
            return Response({"detail": "Perfil de paciente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Filtros
        estado_pago = request.query_params.get("estado_pago")
        estado = request.query_params.get("estado")
        clinica_id = request.query_params.get("clinica_id")

        qs = Cita.objects.filter(paciente=paciente)
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

        # Buscar o crear Paciente si no existe
        paciente, created = Paciente.objects.get_or_create(
            ci=user.ci if user.ci else user.username,
            defaults={
                'nombre': f"{user.first_name} {user.last_name}".strip() or user.username,
                'telefono': user.telefono,
                'fecha_nacimiento': '2000-01-01',
                'clinica_id': 1, # Default temporal, el paciente real no tiene por qué tener una clinica fija en la app
                'strikes_diarios': 0,
            }
        )

        psicologo_username = request.data.get("psicologo_username")
        fecha_hora = request.data.get("fecha_hora")
        motivo = request.data.get("motivo", "")
        monto = request.data.get("monto", "120.00")

        try:
            psicologo = Usuario.objects.get(username=psicologo_username, rol='PSICOLOGO')
        except Usuario.DoesNotExist:
            return Response({"detail": "Especialista no encontrado."}, status=status.HTTP_404_NOT_FOUND)

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
        if psicologo.clinica and psicologo.clinica.admin:
            NotificacionPush.objects.create(
                usuario=psicologo.clinica.admin,
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
        if clinica and clinica.admin:
            NotificacionPush.objects.create(
                usuario=clinica.admin,
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

class MobilePacientePagarAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        cita_id = request.data.get("cita_id")
        metodo_pago = request.data.get("metodo_pago", "STRIPE_MOCK")

        try:
            cita = Cita.objects.get(id=cita_id)
        except Cita.DoesNotExist:
            return Response({"detail": "Cita no encontrada"}, status=status.HTTP_404_NOT_FOUND)

        if cita.estado_pago == 'PAGADO':
            return Response({"detail": "Esta cita ya está pagada."}, status=status.HTTP_400_BAD_REQUEST)

        # Simulamos éxito de Stripe
        cita.estado_pago = 'PAGADO'
        cita.save()

        # Generar Transacción en la Clínica
        if cita.psicologo.clinica:
            cita.psicologo.clinica.saldo += decimal.Decimal(str(cita.monto))
            cita.psicologo.clinica.save()
            TransaccionClinica.objects.create(
                clinica=cita.psicologo.clinica,
                tipo='INGRESO_PACIENTE',
                monto=cita.monto,
                descripcion=f"Pago de cita #{cita.id} - Paciente: {user.username}",
                metodo_pago=metodo_pago
            )

        # Notificación para el paciente
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        NotificacionPush.objects.create(
            usuario=user,
            titulo="Pago Exitoso",
            mensaje=f"Tu pago de ${cita.monto} para la cita con {cita.psicologo.usuario.first_name} {cita.psicologo.usuario.last_name} ha sido procesado."
        )

        # Notificación para el psicólogo
        NotificacionPush.objects.create(
            usuario=cita.psicologo.usuario,
            titulo="Pago Recibido",
            mensaje=f"El paciente {user.first_name} {user.last_name} ha pagado la cita (${cita.monto})."
        )

        # Notificación para la clínica
        if cita.psicologo.clinica and cita.psicologo.clinica.admin:
            NotificacionPush.objects.create(
                usuario=cita.psicologo.clinica.admin,
                titulo="Ingreso por Cita",
                mensaje=f"El paciente {user.first_name} {user.last_name} ha pagado ${cita.monto} por cita con {cita.psicologo.usuario.first_name}."
            )

        return Response({"detail": "Pago procesado exitosamente.", "cita_id": cita.id}, status=status.HTTP_201_CREATED)

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
