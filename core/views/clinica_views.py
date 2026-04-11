# [SPRINT 1 - T024] Registro de Clínica (Tenant): Alta de nuevas clínicas.
# [SPRINT 1 - T017] CRUD de Psicólogos: Gestión de usuarios por clínica.
# [RF-29] Aislamiento SaaS | [RF-28] RBAC | [CU-25]
import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers import ClinicaSerializer, UsuarioSerializer
from core.security.permissions import IsAdmin

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: ADMINISTRACIÓN (TENANTS Y USUARIOS) [SPRINT 1 - T024] [T017]
# ==============================================================================


class ClinicaCreateAPIView(APIView):
    """[SPRINT 1 - T024] [CU-25] [RF-29] Registra un nuevo tenant (clínica)."""

    permission_classes = [IsAdmin]  # [SPRINT 1 - T018] RBAC: Solo admins

    def post(self, request):
        serializer = ClinicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"ADMIN: Nueva clínica creada - {request.data.get('nombre')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioCreateAPIView(APIView):
    """[SPRINT 1 - T017] [RF-04] [RF-28] Registro de psicólogos vinculados al tenant."""

    permission_classes = [IsAdmin]  # [SPRINT 1 - T018] RBAC: Solo admins

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"ADMIN: Nuevo usuario {request.data.get('username')} creado por {request.user.username}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
