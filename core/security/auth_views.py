import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

# ✅ IMPORTACIÓN DIRECTA PARA EVITAR IMPORT CIRCULAR
from core.serializers.usuario_serializer import UsuarioSerializer
from .jwt_serializers import CustomTokenObtainPairSerializer

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: AUTENTICACIÓN Y PERFIL
# ==============================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        logger.info(f"AUTH: Intento de login - Usuario: {request.data.get('username')}")
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            logger.info(
                f"AUTH: Login exitoso - Usuario: {request.data.get('username')}"
            )
        return response


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
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
        except Exception as e:
            logger.error(f"AUTH: Error en logout - {str(e)}")
            return Response(
                {"error": "Token inválido o expirado"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ Retorna la info del usuario autenticado
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
