import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core.models import Paciente, Cita

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: NEGOCIO (DASHBOARD)
# ==============================================================================


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ---------------------------------------------------------
        # SOLUCIÓN BUG: Permite al ADMIN ver un dashboard global
        # ---------------------------------------------------------
        if request.user.rol == "ADMIN":
            total_pacientes = Paciente.objects.count()
            citas_pendientes = Cita.objects.filter(estado="PENDIENTE").count()
            nombre_clinica = "Administración Global (Multi-Tenant)"
        else:
            clinica = request.user.clinica
            if not clinica:
                logger.warning(
                    f"SEGURIDAD: Acceso denegado al Dashboard - Usuario {request.user.username} sin clínica."
                )
                raise PermissionDenied("Su usuario no tiene una clínica asignada.")

            total_pacientes = Paciente.objects.filter(clinica=clinica).count()
            citas_pendientes = Cita.objects.filter(
                paciente__clinica=clinica, estado="PENDIENTE"
            ).count()
            nombre_clinica = clinica.nombre

        return Response(
            {
                "clinica": nombre_clinica,
                "metricas": {
                    "total_pacientes": total_pacientes,
                    "citas_pendientes": citas_pendientes,
                },
            },
            status=status.HTTP_200_OK,
        )
