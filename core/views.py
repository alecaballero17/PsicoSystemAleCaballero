"""
Módulo de vistas y controladores para PsicoSystem SI2.
Contiene tanto las vistas web MVC como los endpoints de la API REST.
"""

import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied, ValidationError

from .models import Paciente, Cita
from .permissions import IsPsicologo, IsAdmin
from .serializers import (
    PacienteSerializer,
    ClinicaSerializer,
    UsuarioSerializer,
    CustomTokenObtainPairSerializer,
)

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


# ==============================================================================
# CAPA API: NEGOCIO (DASHBOARD Y PACIENTES)
# ==============================================================================


class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
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


# ==============================================================================
# VISTA TEMPORAL (Para evitar errores de importación residuales)
# ==============================================================================
class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ✅ AHORA SÍ USAMOS EL SERIALIZER PARA TRAER TODOS LOS DATOS
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
