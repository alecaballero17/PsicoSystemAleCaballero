from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import PacienteForm
from .serializers import PacienteSerializer, PacienteDetalleSerializer
from .models import Paciente, ExpedienteClinico
from apps.P4_IA_Administracion.models import LogAuditoria
from apps.P1_Identidad_Acceso.permissions import (
    HasClinicaAsignada,
    EsPsicologoOAdministrador,
)


@login_required
def registrar_paciente_view(request):
    if not getattr(request.user, "clinica", None):
        messages.error(
            request,
            "ATENCIÓN: Tu cuenta actual no está asignada a ninguna clínica. No puedes registrar pacientes hasta tener una clínica.",
        )
        return redirect("dashboard")

    if request.method == "POST":
        form = PacienteForm(request.POST)
        if form.is_valid():
            # [SaaS Limits Check]
            clinica = request.user.clinica
            plan = clinica.plan_suscripcion if clinica else 'Basico'
            limite = 5 if plan == 'Basico' else (20 if plan == 'Profesional' else 9999)
            actual = Paciente.objects.filter(clinica=clinica).count()
            if actual >= limite:
                messages.error(request, f"Límite excedido: Tu plan actual ({plan}) solo permite registrar hasta {limite} pacientes. Actualiza tu suscripción en la sección correspondiente.")
                return redirect("dashboard")

            paciente = form.save(commit=False)
            paciente.clinica = request.user.clinica
            paciente.save()
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Registró un nuevo paciente: {paciente.nombre}",
            )
            return redirect("dashboard")
    else:
        form = PacienteForm()
    return render(request, "P2_Gestion_Clinica/registrar_paciente.html", {"form": form})


@login_required
def editar_paciente_view(request, pk):
    paciente = get_object_or_404(Paciente, pk=pk, clinica=request.user.clinica)
    if request.method == "POST":
        form = PacienteForm(request.POST, instance=paciente)
        if form.is_valid():
            paciente = form.save()
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Actualizó paciente: {paciente.nombre}",
            )
            return redirect("listar_pacientes")
    else:
        form = PacienteForm(instance=paciente)
    return render(
        request,
        "P2_Gestion_Clinica/editar_paciente.html",
        {"form": form, "paciente": paciente},
    )


@login_required
def listar_pacientes_view(request):
    pacientes = Paciente.objects.filter(clinica=request.user.clinica)
    return render(request, "P2_Gestion_Clinica/paciente_list.html", {"pacientes": pacientes})


class PacienteListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = PacienteSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return Paciente.objects.filter(clinica=self.request.user.clinica).order_by("nombre")

    def perform_create(self, serializer):
        # [SaaS Limits Check]
        clinica = self.request.user.clinica
        plan = clinica.plan_suscripcion if clinica else 'Basico'
        limite = 5 if plan == 'Basico' else (20 if plan == 'Profesional' else 9999)
        actual = Paciente.objects.filter(clinica=clinica).count()
        if actual >= limite:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Límite excedido: Tu plan actual ({plan}) solo permite registrar hasta {limite} pacientes.")

        paciente = serializer.save(clinica=self.request.user.clinica)
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Registró un nuevo paciente (API): {paciente.nombre}",
        )


class PacienteRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return PacienteDetalleSerializer
        return PacienteSerializer

    def get_queryset(self):
        return Paciente.objects.filter(clinica=self.request.user.clinica)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # CU20: Recuperación de Datos Clínicos (Automática)
        ExpedienteClinico.objects.get_or_create(paciente=instance)
        return super().retrieve(request, *args, **kwargs)

    def perform_update(self, serializer):
        paciente = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Actualizó paciente (API): {paciente.nombre}",
        )

# ==============================================================================
# T027: Búsqueda y Filtrado
# ==============================================================================
from django.db.models import Q

class PacienteSearchAPIView(generics.ListAPIView):
    serializer_class = PacienteSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get_queryset(self):
        query = self.request.query_params.get('q', '')
        return Paciente.objects.filter(
            Q(clinica=self.request.user.clinica) &
            (Q(nombre__icontains=query) | Q(ci__icontains=query))
        )

# ==============================================================================
# T026: API de Expediente Clínico
# ==============================================================================
from rest_framework import viewsets
from .models import ExpedienteClinico, NotaClinica, ArchivoAdjunto
from .serializers import (
    ExpedienteClinicoSerializer,
    NotaClinicaSerializer,
    ArchivoAdjuntoSerializer
)

class ExpedienteClinicoViewSet(viewsets.ModelViewSet):
    serializer_class = ExpedienteClinicoSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get_queryset(self):
        return ExpedienteClinico.objects.filter(paciente__clinica=self.request.user.clinica)

class NotaClinicaViewSet(viewsets.ModelViewSet):
    serializer_class = NotaClinicaSerializer
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador]

    def get_queryset(self):
        return NotaClinica.objects.filter(expediente__paciente__clinica=self.request.user.clinica)

    def perform_create(self, serializer):
        serializer.save(psicologo=self.request.user)

class ArchivoAdjuntoViewSet(viewsets.ModelViewSet):
    serializer_class = ArchivoAdjuntoSerializer
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador]

    def get_queryset(self):
        return ArchivoAdjunto.objects.filter(expediente__paciente__clinica=self.request.user.clinica)

# ==============================================================================
# SPRINT 4: APIs de Evolución, Diagnóstico e Historial Completo (CU29)
# ==============================================================================
from .models import Evolucion, DiagnosticoPaciente
from .serializers import EvolucionSerializer, DiagnosticoPacienteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.P3_Logistica_Citas.models import Cita
from apps.P3_Logistica_Citas.serializers import CitaSerializer

class EvolucionViewSet(viewsets.ModelViewSet):
    """T061: CRUD de notas de evolución clínica por sesión."""
    serializer_class = EvolucionSerializer
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador]

    def get_queryset(self):
        qs = Evolucion.objects.filter(paciente__clinica=self.request.user.clinica)
        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        return qs

    def perform_create(self, serializer):
        evolucion = serializer.save(psicologo=self.request.user)
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Registró evolución clínica para {evolucion.paciente.nombre} ({evolucion.fecha_sesion})"
        )

class DiagnosticoPacienteViewSet(viewsets.ModelViewSet):
    """T064: CRUD de diagnóstico global (inicial/final) del paciente."""
    serializer_class = DiagnosticoPacienteSerializer
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador]

    def get_queryset(self):
        qs = DiagnosticoPaciente.objects.filter(paciente__clinica=self.request.user.clinica)
        paciente_id = self.request.query_params.get('paciente')
        if paciente_id:
            qs = qs.filter(paciente_id=paciente_id)
        return qs

    def perform_create(self, serializer):
        dx = serializer.save(psicologo=self.request.user)
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Registró diagnóstico global para {dx.paciente.nombre}"
        )

    def perform_update(self, serializer):
        dx = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Actualizó diagnóstico de {dx.paciente.nombre} (estado: {dx.get_estado_display()})"
        )

class HistorialCompletoAPIView(APIView):
    """T062: Endpoint que devuelve el historial clínico completo de un paciente."""
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador, HasClinicaAsignada]

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente, pk=paciente_id, clinica=request.user.clinica)

        # Diagnóstico global
        try:
            dx_global = DiagnosticoPaciente.objects.get(paciente=paciente)
            dx_data = DiagnosticoPacienteSerializer(dx_global).data
        except DiagnosticoPaciente.DoesNotExist:
            dx_data = None

        # Evoluciones
        evoluciones = Evolucion.objects.filter(paciente=paciente).order_by('-fecha_sesion')
        evo_data = EvolucionSerializer(evoluciones, many=True).data

        # Citas
        citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')
        citas_data = CitaSerializer(citas, many=True).data

        return Response({
            'paciente': {
                'id': paciente.id,
                'nombre': paciente.nombre,
                'ci': paciente.ci,
                'fecha_nacimiento': str(paciente.fecha_nacimiento),
                'telefono': paciente.telefono,
                'motivo_consulta': paciente.motivo_consulta,
            },
            'diagnostico_global': dx_data,
            'evoluciones': evo_data,
            'citas': citas_data,
        })

class AnaliticaClinicaAPIView(APIView):
    """T071: Métricas de analítica clínica para el dashboard."""
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador, HasClinicaAsignada]

    def get(self, request):
        clinica = request.user.clinica

        total_pacientes = Paciente.objects.filter(clinica=clinica).count()

        # Diagnósticos por estado
        en_tratamiento = DiagnosticoPaciente.objects.filter(paciente__clinica=clinica, estado='EN_TRATAMIENTO').count()
        alta = DiagnosticoPaciente.objects.filter(paciente__clinica=clinica, estado='ALTA').count()
        abandono = DiagnosticoPaciente.objects.filter(paciente__clinica=clinica, estado='ABANDONO').count()
        sin_diagnostico = total_pacientes - (en_tratamiento + alta + abandono)

        # Distribución de estados de ánimo (últimas evoluciones)
        from django.db.models import Count
        estados_animo = list(
            Evolucion.objects.filter(paciente__clinica=clinica)
            .values('estado_animo')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        # Últimos diagnósticos IA
        from apps.P4_IA_Administracion.models import DiagnosticoIA
        ultimos_ia = list(
            DiagnosticoIA.objects.filter(psicologo__clinica=clinica)
            .order_by('-fecha_analisis')[:10]
            .values('id', 'paciente__nombre', 'resultado_ia', 'probabilidad_acierto', 'fecha_analisis')
        )

        # Últimas evoluciones
        ultimas_evoluciones = EvolucionSerializer(
            Evolucion.objects.filter(paciente__clinica=clinica)[:10],
            many=True
        ).data

        return Response({
            'total_pacientes': total_pacientes,
            'en_tratamiento': en_tratamiento,
            'alta': alta,
            'abandono': abandono,
            'sin_diagnostico': sin_diagnostico,
            'estados_animo': estados_animo,
            'ultimos_ia': ultimos_ia,
            'ultimas_evoluciones': ultimas_evoluciones,
        })


from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from apps.P1_Identidad_Acceso.models import Clinica
from .serializers import PacienteRegistroPublicoSerializer
import logging

logger = logging.getLogger(__name__)

class PacienteRegistroPublicoAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PacienteRegistroPublicoSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            logger.info("NUEVO PACIENTE AUTO-REGISTRADO: %s", result["email"])
            return Response(
                {"message": "Registro completado con éxito.", "data": result},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssociateClinicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        clinica_id = request.data.get('clinica_id')
        if not clinica_id:
            return Response({"detail": "Se requiere clinica_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clinica = Clinica.objects.get(id=clinica_id)
            user = request.user
            
            user.clinica = clinica
            user.save()

            try:
                paciente = Paciente.objects.get(ci=user.username)
            except Paciente.DoesNotExist:
                paciente = Paciente.objects.filter(ci=user.username).first()

            if paciente:
                paciente.clinica = clinica
                paciente.save()

            return Response({
                "message": f"Vínculo exitoso con {clinica.nombre}",
                "clinica_id": clinica.id,
                "clinica_nombre": clinica.nombre
            }, status=status.HTTP_200_OK)

        except Clinica.DoesNotExist:
            return Response({"detail": "La clínica no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MiHistorialClinicoAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            paciente = Paciente.objects.get(ci=request.user.username)
        except Paciente.DoesNotExist:
            paciente = Paciente.objects.filter(ci=request.user.username).first()

        if not paciente:
            return Response({"detail": "Paciente no encontrado."}, status=status.HTTP_404_NOT_FOUND)

        # Diagnóstico global
        try:
            from .models import DiagnosticoPaciente
            from .serializers import DiagnosticoPacienteSerializer
            dx_global = DiagnosticoPaciente.objects.get(paciente=paciente)
            dx_data = DiagnosticoPacienteSerializer(dx_global).data
        except:
            dx_data = None

        # Evoluciones
        try:
            from .models import Evolucion
            from .serializers import EvolucionSerializer
            evoluciones = Evolucion.objects.filter(paciente=paciente).order_by('-fecha_sesion')
            evo_data = EvolucionSerializer(evoluciones, many=True).data
        except:
            evo_data = []

        # Citas
        try:
            from apps.P3_Logistica_Citas.models import Cita
            from apps.P3_Logistica_Citas.serializers import CitaSerializer
            citas = Cita.objects.filter(paciente=paciente).order_by('-fecha_hora')
            citas_data = CitaSerializer(citas, many=True).data
        except:
            citas_data = []

        return Response({
            'paciente': {
                'id': paciente.id,
                'nombre': paciente.nombre,
                'ci': paciente.ci,
                'fecha_nacimiento': str(paciente.fecha_nacimiento),
                'telefono': paciente.telefono,
                'motivo_consulta': paciente.motivo_consulta,
            },
            'diagnostico_global': dx_data,
            'evoluciones': evo_data,
            'citas': citas_data,
        })

