"""
[SPRINT 1 - T011] Core de Seguridad JWT: Vistas de autenticación stateless.
[SPRINT 1 - T022] Blacklisting de Tokens: Logout con revocación.
[SPRINT 1 - T023] Logging y Auditoría: Trazas de eventos de acceso (RF-30).
"""

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from core.serializers.usuario_serializer import UsuarioSerializer
from .jwt_serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: AUTENTICACIÓN Y PERFIL [SPRINT 1 - T011] [RF-01] [CU-01]
# ==============================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """[SPRINT 1 - T011] [RF-01] [CU-01] Login JWT con inyección de rol y clínica."""

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        """Autentica al usuario y retorna tokens JWT con metadatos de rol y clínica."""
        # [SPRINT 1 - T023] [RF-30] Registro de evento de acceso
        logger.info(
            "AUTH: Intento de login - Usuario: %s",
            request.data.get("username"),
        )
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(
                "AUTH: Login exitoso - Usuario: %s",
                request.data.get("username"),
            )
        return response


class LogoutAPIView(APIView):
    """[SPRINT 1 - T022] [CU-04] Terminación de sesión con blacklist de refresh token."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Invalida el refresh token agregándolo a la blacklist."""
        try:
            refresh_token = request.data.get("refresh")
            if not refresh_token:
                return Response(
                    {"error": "Token de refresco es requerido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT
            )
        except TokenError as exc:
            logger.error("AUTH: Error en logout - %s", exc)
            return Response(
                {"error": "Token inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeAPIView(APIView):
    """[SPRINT 1 - T011] [RF-03] Perfil del usuario autenticado."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Retorna la información serializada del usuario autenticado."""
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
