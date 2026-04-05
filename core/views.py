"""
Módulo de vistas y controladores para PsicoSystem SI2.
Contiene tanto las vistas web MVC como los endpoints de la API REST.
"""

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import PermissionDenied

from .models import Paciente, Cita
from .permissions import IsPsicologo, IsAdmin
from .serializers import (
    PacienteSerializer,
    ClinicaSerializer,
    UsuarioSerializer,
    CustomTokenObtainPairSerializer,
)  # NUEVO: Importación necesaria para T014


# Vistas removidas para cumplimiento de Arquitectura REST (API REST-only)
# CU-25 y CU-02 se manejan via ClinicaCreateAPIView y UsuarioCreateAPIView.


# RF-02 y T014 se manejan via PacienteCreateAPIView y PacienteListAPIView.
# T007 (Dashboard) se maneja via DashboardAPIView.


# ==============================================================================
# CAPA API: SERVICIOS REST (DESACOPLAMIENTO)
# SPRINT 1 | T008 (Arquitectura REST) | T011 (Autenticación JWT) | T014 (Validación)
# ==============================================================================


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Trazabilidad: RF-01, RF-28
    Vista JWT personalizada para retornar tokens que incluyen los roles de usuario.
    """

    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        print(f"DEBUG: Intento de login para usuario: {request.data.get('username')}")
        response = super().post(request, *args, **kwargs)
        print(f"DEBUG: Resultado login: {response.status_code}")
        return response


class LogoutAPIView(APIView):
    """
    CU-04: Cierre de Sesión (API)
    Invalida el Token de Refresco en la lista negra.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(
                {"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT
            )
        except Exception:
            return Response(
                {"error": "Token inválido"}, status=status.HTTP_400_BAD_REQUEST
            )


class MeAPIView(APIView):
    """
    RF-03: Perfil de Usuario | T011
    Retorna los datos del usuario autenticado.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UsuarioSerializer(request.user)
        return Response(serializer.data)


class DashboardAPIView(APIView):
    """
    RNF-01: Interoperabilidad (Servicio para React/Flutter)
    T008: Implementación de arquitectura orientada a servicios.
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        """
        Retorna las métricas del dashboard filtradas por la clínica del usuario.
        """
        clinica = request.user.clinica  # RF-29: Multi-tenancy

        # SOLUCIÓN AL BUG: Si no hay clínica, lanzamos error 403 explícito
        if not clinica:
            raise PermissionDenied(
                "Su usuario no tiene una clínica asignada. Contacte al administrador."
            )

        total_pacientes = Paciente.objects.filter(clinica=clinica).count()
        citas_pendientes = Cita.objects.filter(
            paciente__clinica=clinica, estado="PENDIENTE"
        ).count()

        data = {
            "clinica": clinica.nombre,
            "metricas": {
                "total_pacientes": total_pacientes,
                "citas_pendientes": citas_pendientes,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


class PacienteCreateAPIView(APIView):
    """
    T014: Desarrollo de funcionalidades de interoperabilidad.
    CU-02: Registro de Paciente vía API (Móvil/React).
    CORRECCIÓN DE AUDITORÍA: Validación de pertenencia organizacional (RF-29).
    """

    permission_classes = [IsPsicologo]

    def post(self, request):
        # --- PASO 1: VALIDACIÓN DE SEGURIDAD (RNF-03 / RF-29) ---
        # Si el usuario no tiene clínica, lanzamos error antes de procesar nada.
        # Esto evita que serializer.save() falle por un IntegrityError de base de datos.
        if not request.user.clinica:
            raise PermissionDenied(
                "No puede registrar pacientes: Su cuenta no está vinculada a ninguna clínica."
            )

        # --- PASO 2: INSTANCIACIÓN Y VALIDACIÓN DE DATOS (RNF-08) ---
        serializer = PacienteSerializer(data=request.data)

        if serializer.is_valid():
            # --- PASO 3: PERSISTENCIA MULTI-TENANT (RF-29) ---
            # Inyectamos la clínica del usuario autenticado automáticamente.
            serializer.save(clinica=request.user.clinica)

            return Response(
                {
                    "message": "Paciente registrado exitosamente vía REST API",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        # Si los datos son inválidos (ej: CI ya existe), devolvemos el error 400.
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# RESOLUCIÓN INCUMPLIMIENTO #3: ENDPOINTS DE ESCRITURA API (INTEROPERABILIDAD)
# ==============================================================================


class ClinicaCreateAPIView(APIView):
    """
    T001 / RF-29: Registro de Clínica vía API.
    Permite que sistemas externos registren organizaciones en la plataforma.
    """

    # En este caso, el registro de clínica suele ser público o de admin
    permission_classes = [IsAdmin]

    def post(self, request):
        """Crea una nueva clínica mediante JSON."""
        serializer = ClinicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Clínica registrada vía API", "data": serializer.data},
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioCreateAPIView(APIView):
    """
    T001 / RF-28: Registro de Psicólogo/Usuario vía API.
    Cumple con la arquitectura híbrida al permitir registros JSON.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        """Registra un nuevo usuario mediante JSON."""
        serializer = UsuarioSerializer(data=request.data)
        if serializer.is_valid():
            # Aquí podrías añadir lógica extra para roles si fuera necesario
            serializer.save()
            return Response(
                {
                    "message": "Usuario/Psicólogo registrado vía API",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PacienteListAPIView(APIView):
    """
    T014: Endpoint para listar pacientes del Tenant actual.
    Este es el que necesita tu Dashboard de React para llenar la tabla.
    """

    permission_classes = [IsPsicologo]

    def get(self, request):
        """
        Obtiene la lista de pacientes registrados en la clínica del usuario autenticado.
        """
        # RF-29: Filtramos para que solo vea los pacientes de SU clínica
        clinica = request.user.clinica
        if not clinica:
            raise PermissionDenied(
                "No se puede listar pacientes: Usuario sin clínica asignada."
            )

        pacientes = Paciente.objects.filter(clinica=clinica)
        serializer = PacienteSerializer(pacientes, many=True)

        # Esto es lo que React va a recibir y mapear en la tabla
        return Response(serializer.data, status=status.HTTP_200_OK)
