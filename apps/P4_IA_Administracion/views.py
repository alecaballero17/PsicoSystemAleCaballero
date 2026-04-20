from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita
from .models import LogAuditoria

@login_required
def dashboard_view(request):
    clinica = request.user.clinica

    total_pacientes = Paciente.objects.filter(clinica=clinica).count() if clinica else 0
    citas_pendientes = Cita.objects.filter(
        paciente__clinica=clinica, estado="PENDIENTE"
    ).count() if clinica else 0
    
    ultimos_logs = LogAuditoria.objects.filter(usuario__clinica=clinica)[:5] if clinica else LogAuditoria.objects.none()

    contexto = {
        "total_pacientes": total_pacientes,
        "citas_pendientes": citas_pendientes,
        "clinica_nombre": clinica.nombre if clinica else "S/C",
        "ultimos_logs": ultimos_logs,
    }
    return render(request, "P4_IA_Administracion/dashboard.html", contexto)

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get(self, request):
        clinica = request.user.clinica
        total_pacientes = Paciente.objects.filter(clinica=clinica).count() if clinica else 0
        citas_pendientes = Cita.objects.filter(
            paciente__clinica=clinica, estado="PENDIENTE"
        ).count() if clinica else 0

        data = {
            "clinica": clinica.nombre if clinica else "Sin Clínica",
            "metricas": {
                "total_pacientes": total_pacientes,
                "citas_pendientes": citas_pendientes,
            },
        }
        return Response(data, status=status.HTTP_200_OK)
