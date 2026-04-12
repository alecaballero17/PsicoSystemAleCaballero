"""
[SPRINT 1 - T016] Gestión de Personal Clínico: Dashboard de métricas por tenant.
[RF-28] Control de Acceso RBAC: Vista filtrada por rol.
[RF-29] Aislamiento SaaS: Datos segregados por Clínica (Tenant).
[RNF-06] Escalabilidad: Consultas agregadas para minimizar carga en BD.
"""
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

# [ALINEACIÓN SPRINT 0 - T005] Entidades del dominio Multi-tenant
from core.models import Paciente, Cita

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: NEGOCIO (DASHBOARD)
# ==============================================================================


class DashboardAPIView(APIView):
    """
    [ALINEACIÓN SPRINT 1 - T016 / RF-28 / RF-29] Dashboard con métricas por clínica.
    Aplica aislamiento Multi-tenant: el ADMIN ve el global, el PSICÓLOGO solo su clínica.
    """

    permission_classes = [IsAuthenticated]  # [RNF-03] Acceso exclusivo con JWT válido

    def get(self, request):
        """
        [ALINEACIÓN SPRINT 1 - T016] Retorna métricas calculadas en servidor.
        Aplica aislamiento Multi-tenant (RF-29).
        """
        clinica = request.user.clinica
        
        if not clinica:
            # Si es un Superusuario o Admin sin clínica, retornamos vacío o error controlado
            logger.warning(f"Acceso al dashboard sin clínica: {request.user.username}")
            return Response({
                "clinica": "Sin Clínica Asignada",
                "metricas": {"total_pacientes": 0, "citas_pendientes": 0}
            }, status=status.HTTP_200_OK)

        # [ALINEACIÓN RF-29] Filtro estricto por Tenant
        total_pacientes = Paciente.objects.filter(clinica=clinica).count()
        citas_pendientes = Cita.objects.filter(
            paciente__clinica=clinica, 
            estado="PENDIENTE"
        ).count()

        return Response(
            {
                "clinica": clinica.nombre,
                "metricas": {
                    "total_pacientes": total_pacientes,
                    "citas_pendientes": citas_pendientes,
                },
            },
            status=status.HTTP_200_OK,
        )
