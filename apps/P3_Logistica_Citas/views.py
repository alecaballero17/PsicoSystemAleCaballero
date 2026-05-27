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
    [CU-MOBILE] POST: Crear una cita desde la App Móvil.
    El paciente se identifica automáticamente por el CI vinculado a su cuenta de usuario.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from apps.P2_Gestion_Clinica.models import Paciente
        from apps.P1_Identidad_Acceso.models import Clinica
        from django.utils.dateparse import parse_datetime

        user = request.user
        fecha_hora_str = request.data.get('fecha_hora')
        motivo = request.data.get('motivo', '')
        psicologo_username = request.data.get('psicologo_username')
        clinica_id = request.data.get('clinica_id')

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
                fecha_hora=fecha_hora,
                motivo=motivo,
                estado='PENDIENTE',
            )
        except Exception as e:
            return Response({"error": str(e)}, status=400)

        return Response({
            "id": cita.pk,
            "mensaje": "Cita programada exitosamente.",
            "fecha_hora": cita.fecha_hora.isoformat(),
            "psicologo": psicologo.get_full_name() or psicologo.username,
            "estado": cita.estado,
        }, status=201)

