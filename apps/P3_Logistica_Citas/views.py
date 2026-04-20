from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

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
