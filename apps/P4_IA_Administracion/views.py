from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita
from .models import LogAuditoria

class LogAuditoriaAPIView(APIView):
    """
    Endpoint de bitácora exclusivo para el Administrador de la clínica.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def get(self, request):
        clinica = request.user.clinica
        logs = LogAuditoria.objects.filter(usuario__clinica=clinica).order_by('-fecha')[:50]
        
        data = [
            {
                "fecha": log.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": getattr(log.usuario, "username", "Desconocido") if log.usuario else "Desconocido",
                "accion": log.accion
            }
            for log in logs
        ]
        return Response(data, status=status.HTTP_200_OK)

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
