from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import PacienteForm
from .serializers import PacienteSerializer
from .models import Paciente
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
        paciente = serializer.save(clinica=self.request.user.clinica)
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Registró un nuevo paciente (API): {paciente.nombre}",
        )


class PacienteRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PacienteSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return Paciente.objects.filter(clinica=self.request.user.clinica)

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
# T015: Registro Público Móvil (App) y Vinculación
# ==============================================================================
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import PacienteRegistroPublicoSerializer
from apps.P1_Identidad_Acceso.models import Clinica, Usuario

logger = logging.getLogger(__name__)

class PacienteRegistroPublicoAPIView(APIView):
    """
    [SPRINT 1 - T015] [CU-02] Endpoint público para la autogestión y registro
    de credenciales por parte del propio paciente desde la app móvil.
    """
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
    """
    [RF-29] Vinculación post-login para usuarios huérfanos en Flutter.
    Asocia una clínica al usuario y al objeto Paciente correspondiente.
    """
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        clinica_id = request.data.get('clinica_id')
        if not clinica_id:
            return Response({"detail": "Se requiere clinica_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clinica = Clinica.objects.get(id=clinica_id)
            user = request.user
            
            # 1. Actualizar el usuario
            user.clinica = clinica
            user.save()

            # 2. Intentar actualizar el objeto Paciente si existe (basado en el email)
            try:
                paciente = Paciente.objects.get(ci=user.username)
            except Paciente.DoesNotExist:
                # Fallback
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
