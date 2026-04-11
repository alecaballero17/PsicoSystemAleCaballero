import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core.models import Paciente

# ✅ IMPORTACIÓN DIRECTA PARA EVITAR IMPORT CIRCULAR
from core.serializers.paciente_serializer import PacienteSerializer
from core.security.permissions import IsPsicologo

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: NEGOCIO (PACIENTES)
# ==============================================================================


class PacienteListAPIView(APIView):
    permission_classes = [IsPsicologo]

    def get(self, request):
        clinica = request.user.clinica
        if not clinica:
            raise PermissionDenied("Usuario sin clínica asignada.")

        pacientes = Paciente.objects.filter(clinica=clinica).order_by("-id")
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PacienteCreateAPIView(APIView):
    permission_classes = [IsPsicologo]

    def post(self, request):
        if not request.user.clinica:
            raise PermissionDenied(
                "No puede registrar pacientes sin vinculación clínica."
            )

        serializer = PacienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinica=request.user.clinica)
            logger.info(
                f"DATA: Nuevo paciente registrado por {request.user.username} en {request.user.clinica.nombre}"
            )
            return Response(
                {
                    "message": "Paciente registrado exitosamente",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
