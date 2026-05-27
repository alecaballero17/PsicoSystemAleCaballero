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
    citas = Cita.objects.filter(paciente__clinica=request.user.clinica).select_related(
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
            Cita.objects.filter(paciente__clinica=self.request.user.clinica)
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
            paciente__clinica=self.request.user.clinica
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
        return Cita.objects.filter(paciente__clinica=self.request.user.clinica)

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

        # Filtros opcionales
        estado = request.query_params.get('estado')
        estado_pago = request.query_params.get('estado_pago')
        clinica_id = request.query_params.get('clinica_id')

        qs = Cita.objects.filter(paciente=paciente).select_related('psicologo', 'clinica', 'paciente__clinica').order_by('-fecha_hora')
        if estado:
            qs = qs.filter(estado=estado)
        else:
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
                "psicologo": cita.psicologo.get_full_name() or cita.psicologo.username,
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

        # ── Notificación in-app: aparece en la campanita del paciente ──
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        from django.utils import timezone as tz_now

        fecha_local = tz_now.localtime(cita.fecha_hora)
        NotificacionPush.objects.create(
            usuario=user,
            titulo="✅ Cita Programada",
            mensaje=(
                f"Tu cita con {psicologo.get_full_name() or psicologo.username} "
                f"fue agendada para el {fecha_local.strftime('%d/%m/%Y a las %H:%M')}. "
                f"Motivo: {motivo or 'Sin especificar'}."
            ),
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

        # Notificación in-app
        fecha_local = tz.localtime(cita.fecha_hora)
        NotificacionPush.objects.create(
            usuario=user,
            titulo="❌ Cita Cancelada",
            mensaje=(
                f"Tu cita con {cita.psicologo.get_full_name() or cita.psicologo.username} "
                f"del {fecha_local.strftime('%d/%m/%Y a las %H:%M')} ha sido cancelada."
            ),
        )

        return Response({"mensaje": "Cita cancelada exitosamente.", "estado": cita.estado}, status=200)

class MobileCitaPagarAPIView(APIView):
    """
    [CU-MOBILE] POST: Pagar una cita desde la App Móvil.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.P2_Gestion_Clinica.models import Paciente
        from apps.P1_Identidad_Acceso.models import NotificacionPush
        user = request.user
        cita_id = request.data.get('cita_id')
        metodo_pago = request.data.get('metodo_pago')
        
        try:
            paciente = Paciente.objects.get(ci=user.ci)
            cita = Cita.objects.get(pk=cita_id, paciente=paciente)
        except (Paciente.DoesNotExist, Cita.DoesNotExist):
            return Response({"error": "Cita no encontrada o no te pertenece."}, status=404)

        if cita.estado_pago == 'PAGADO':
            return Response({"error": "Esta cita ya está pagada."}, status=400)

        cita.estado_pago = 'PAGADO'
        if cita.estado == 'PENDIENTE':
            cita.estado = 'PROGRAMADA'
        cita.save(update_fields=['estado_pago', 'estado'])

        # Notificación
        NotificacionPush.objects.create(
            usuario=user,
            titulo="✅ Pago Exitoso",
            mensaje=f"Tu pago de ${cita.monto} para la cita con {cita.psicologo.get_full_name()} ha sido procesado correctamente.",
        )

        return Response({"mensaje": "Pago exitoso", "estado_pago": cita.estado_pago, "estado": cita.estado}, status=201)
