import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.serializers import ClinicaSerializer, UsuarioSerializer
from core.security.permissions import IsAdmin

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: ADMINISTRACIÓN (TENANTS Y USUARIOS)
# ==============================================================================


class ClinicaCreateAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = ClinicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(f"ADMIN: Nueva clínica creada - {request.data.get('nombre')}")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioCreateAPIView(APIView):
    permission_classes = [IsAdmin]

    def post(self, request):
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                f"ADMIN: Nuevo usuario {request.data.get('username')} creado por {request.user.username}"
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
