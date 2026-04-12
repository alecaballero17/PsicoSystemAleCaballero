"""
[SPRINT 1 - T014] Endpoints de Registro: Persistencia y serialización de pacientes.
[RF-02] Registro de Pacientes | [RF-29] Aislamiento SaaS | [CU-02]
# [SEGURIDAD RNF-03] - Aislamiento de Capas: El Admin gestiona el Tenant, el Psicólogo gestiona la Privacidad Clínica.
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import PermissionDenied

from core.models import Paciente

# ✅ IMPORTACIÓN DIRECTA PARA EVITAR IMPORT CIRCULAR
from core.serializers.paciente_serializer import PacienteSerializer, PacienteRegistroPublicoSerializer
from core.security.permissions import IsPsicologo, IsAdmin
from rest_framework.permissions import AllowAny, IsAuthenticated

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: NEGOCIO (PACIENTES)
# ==============================================================================


class PacienteListAPIView(APIView):
    """[SPRINT 1 - T014] [RF-02] Lista pacientes filtrados por tenant."""
    # [SEGURIDAD RNF-03] - Aislamiento de Capas: El Admin gestiona el Tenant, el Psicólogo gestiona la Privacidad Clínica.

    permission_classes = [IsPsicologo]

    def get(self, request):
        """Retorna los pacientes activos de la clínica del usuario autenticado."""
        clinica = request.user.clinica
        if not clinica:
            raise PermissionDenied("Usuario sin clínica asignada.")

        # [ALINEACIÓN RF-29] Aislamiento de Tenant | [ALINEACIÓN RF-30] Borrado Lógico
        pacientes = Paciente.objects.filter(
            clinica=clinica,
            activo=True
        ).order_by("-id")
        serializer = PacienteSerializer(pacientes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PacienteCreateAPIView(APIView):
    """[SPRINT 1 - T014] [RF-02] [CU-02] Registra un paciente en el tenant."""

    permission_classes = [IsPsicologo]

    def post(self, request):
        """Crea un paciente asignándolo automáticamente a la clínica del usuario."""
        if not request.user.clinica:
            raise PermissionDenied(
                "No puede registrar pacientes sin vinculación clínica."
            )

        serializer = PacienteSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(clinica=request.user.clinica)
            logger.info(
                "DATA: Nuevo paciente registrado por %s en %s",
                request.user.username,
                request.user.clinica.nombre,
            )
            return Response(
                {
                    "message": "Paciente registrado exitosamente",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            serializer.errors, status=status.HTTP_400_BAD_REQUEST
        )


class PacienteRegistroPublicoAPIView(APIView):
    """
    [SPRINT 1 - T015] [CU-02] Endpoint público para la autogestión y registro
    de credenciales por parte del propio paciente.
    """
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PacienteRegistroPublicoSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            logger.info("NUEVO PACIENTE AUTO-REGISTRADO: %s", result["email"])
            return Response(
                {"message": "Registro completado con éxito.", "data": result},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AssociateClinicAPIView(APIView):
    """
    [RF-29] Vinculación post-login para usuarios huérfanos en Flutter.
    Asocia una clínica al usuario y al objeto Paciente correspondiente.
    """
    from rest_framework.permissions import IsAuthenticated
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        clinica_id = request.data.get('clinica_id')
        if not clinica_id:
            return Response({"detail": "Se requiere clinica_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            from core.models import Clinica, Usuario, Paciente
            clinica = Clinica.objects.get(id=clinica_id)
            user = request.user
            
            # 1. Actualizar el usuario
            user.clinica = clinica
            user.save()

            # 2. Intentar actualizar el objeto Paciente si existe (basado en el email)
            try:
                paciente = Paciente.objects.get(email=user.email)
            except Paciente.DoesNotExist:
                # Fallback por ci si el campo de email no estuviese
                paciente = Paciente.objects.filter(ci=user.username).first()

            if paciente:
                paciente.clinica = clinica
                paciente.save()

            return Response({
                "message": f"Vínculo exitoso con {clinica.nombre}",
                "clinica_id": clinica.id,
                "clinica_nombre": clinica.nombre
            }, status=status.HTTP_200_OK)

        except Clinica.DoesNotExist:
            return Response({"detail": "La clínica no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class PacienteDeleteAPIView(APIView):
    """
    [T014/T017] [RF-28] [RF-30] Borrado Seguro de Pacientes.
    Solo accesible para Administradores de la clínica.
    """
    permission_classes = [IsAdmin]

    def delete(self, request, pk):
        """
        [ALINEACIÓN RF-30] - El borrado lógico de pacientes garantiza la integridad 
        del historial clínico para futuras auditorías.
        """
        try:
            paciente = Paciente.objects.get(pk=pk, clinica=request.user.clinica)
            
            # Aplicamos Soft Delete
            paciente.activo = False
            paciente.save()

            logger.info(f"AUDITORÍA RF-30: Paciente #{pk} dado de baja por ADMIN {request.user.username}")
            
            return Response(
                {"message": "Paciente dado de baja exitosamente (Soft Delete)."},
                status=status.HTTP_200_OK
            )
        except Paciente.DoesNotExist:
            return Response(
                {"detail": "El expediente no existe o no tiene permisos sobre él."},
                status=status.HTTP_404_NOT_FOUND
            )
