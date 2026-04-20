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


class PacienteRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
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
