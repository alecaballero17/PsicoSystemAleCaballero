from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from rest_framework import generics, viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.P1_Identidad_Acceso.permissions import (
    HasClinicaAsignada,
    EsPsicologoOAdministrador,
)
from apps.P4_IA_Administracion.models import LogAuditoria

from .forms import CitaForm
from .models import Cita, ListaEspera
from .serializers import CitaSerializer, ListaEsperaSerializer


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


# ==============================================================================
# API REST — CITAS (RF-06, RF-07, RF-08, T030)
# ==============================================================================
class CitaListCreateAPIView(generics.ListCreateAPIView):
    """
    GET: Lista citas filtradas por tenant. Soporta filtros de calendario (RF-08).
    POST: Crea cita con validación de colisiones (T030).
    """
    serializer_class = CitaSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        qs = (
            Cita.objects.filter(paciente__clinica=self.request.user.clinica)
            .select_related("paciente", "psicologo")
            .order_by("fecha_hora")
        )

        # RF-08: Filtros de calendario para Agenda Dinámica
        fecha_inicio = self.request.query_params.get("fecha_inicio")
        fecha_fin = self.request.query_params.get("fecha_fin")
        psicologo_id = self.request.query_params.get("psicologo_id")
        estado = self.request.query_params.get("estado")

        if fecha_inicio:
            qs = qs.filter(fecha_hora__date__gte=fecha_inicio)
        if fecha_fin:
            qs = qs.filter(fecha_hora__date__lte=fecha_fin)
        if psicologo_id:
            qs = qs.filter(psicologo_id=psicologo_id)
        if estado:
            qs = qs.filter(estado=estado)

        return qs

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


class CitaRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET/PUT/PATCH: Detalle y actualización de cita.
    DELETE: Soft-cancel — cambia estado a CANCELADA (RF-07, CU13).
    """
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

    def perform_destroy(self, instance):
        """RF-07 / CU13: Soft-cancel — no eliminamos, cambiamos estado."""
        instance.estado = "CANCELADA"
        instance.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Canceló cita (API): id={instance.pk} — Paciente: {instance.paciente.nombre}",
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"detail": "Cita cancelada exitosamente.", "estado": "CANCELADA"},
            status=status.HTTP_200_OK,
        )


# ==============================================================================
# API REST — LISTA DE ESPERA (T031)
# ==============================================================================
class ListaEsperaViewSet(viewsets.ModelViewSet):
    """
    T031: CRUD de Lista de Espera. Ordenado por prioridad + fecha de registro.
    """
    serializer_class = ListaEsperaSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return ListaEspera.objects.filter(
            paciente__clinica=self.request.user.clinica,
            activo=True,
        ).select_related("paciente").order_by("prioridad", "fecha_registro")

    def perform_create(self, serializer):
        espera = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Añadió a lista de espera: {espera.paciente.nombre} (Prioridad: {espera.prioridad})",
        )

