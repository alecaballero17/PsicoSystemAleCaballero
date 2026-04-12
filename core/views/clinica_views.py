"""
[SPRINT 1 - T024] Registro de Clínica (Tenant): Alta de nuevas clínicas.
[SPRINT 1 - T017] CRUD de Psicólogos: Gestión de usuarios por clínica.
[RF-29] Aislamiento SaaS | [RF-28] RBAC | [CU-25] | [CU-05]
"""

import logging

from django.db import transaction
from django.contrib.auth.hashers import make_password
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics
from rest_framework.permissions import AllowAny

from core.models import Usuario, Clinica, PlanSuscripcion, Suscripcion
from core.serializers import ClinicaSerializer, UsuarioSerializer
from core.security.permissions import IsAdmin

logger = logging.getLogger(__name__)

# ==============================================================================
# CAPA API: ADMINISTRACIÓN (TENANTS Y USUARIOS) [SPRINT 1 - T024] [T017] [CU-05]
# ==============================================================================


class ClinicaCreateAPIView(APIView):
    """[SPRINT 1 - T024] [CU-25] [RF-29] Registra un nuevo tenant (clínica)."""

    # [FIX] Endpoint público: no debe requerir autenticación
    authentication_classes = []

    def get_permissions(self):
        # [RF-29] [CU-25] El onboarding B2B debe ser público
        return [AllowAny()]

    def get(self, request):  # pylint: disable=unused-argument
        """[SPRINT 1 - T015] Lista clínicas activas para el dropdown de registro público."""
        clinicas = Clinica.objects.all().values("id", "nombre")
        return Response(clinicas, status=status.HTTP_200_OK)

    def post(self, request):
        """
        [CIERRE SPRINT 1] Flujo SaaS integrado según Requerimientos 3.2 y RF-29.
        Crea atómicamente la clínica, asigna suscripción y crea el usuario admin.
        """
        clinica_data = request.data.get("clinica", {})
        admin_data = request.data.get("admin", {})
        plan_id = request.data.get("plan_id")

        if not clinica_data or not admin_data or not plan_id:
            return Response(
                {"detail": "Debe proveer datos de clínica, administrador y plan_id."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        audit_logger = logging.getLogger("audit")

        try:
            with transaction.atomic():
                # 1. Crear Tenant (Clínica)
                clinica = Clinica.objects.create(**clinica_data)

                # 2. Crear Suscripción asociada a la Clínica
                plan = PlanSuscripcion.objects.get(id=plan_id)
                Suscripcion.objects.create(clinica=clinica, plan=plan, estado="ACTIVA")

                # 3. Crear Primer Usuario (Admin del Tenant)
                admin_username = admin_data.get("username")
                admin_password = admin_data.get("password")
                admin_email = admin_data.get("email", "")

                if not admin_username or not admin_password:
                    raise ValueError("El administrador requiere username y password.")

                Usuario.objects.create(
                    username=admin_username,
                    email=admin_email,
                    password=make_password(admin_password),
                    clinica=clinica,
                    rol="ADMIN",
                )

                audit_logger.info(
                    "ALTA SaaS B2B: Nueva clínica '%s' registrada con éxito. Plan: %s",
                    clinica.nombre,
                    plan.nombre,
                )
                return Response(
                    {
                        "detail": "Clínica, Suscripción y cuenta de Administrador "
                        "creados exitosamente."
                    },
                    status=status.HTTP_201_CREATED,
                )
        except PlanSuscripcion.DoesNotExist:  # pylint: disable=no-member
            return Response(
                {"detail": "El Plan seleccionado no existe."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except Exception as e:  # pylint: disable=broad-except
            logger.error("Error en alta B2B: %s", str(e))
            return Response(
                {"detail": f"Error registrando el Tenant: {str(e)}"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class ClinicaConfigAPIView(generics.RetrieveUpdateAPIView):
    """
    [RF-29] Mantenimiento de Clínica del administrador en sesión.
    No admite acceso público ni manipulación de terceros.
    """

    serializer_class = ClinicaSerializer

    def get_permissions(self):
        # [RF-29] Todos en la clínica pueden ver su perfil, pero solo el Admin lo puede editar
        from core.security.permissions import IsPsicologo, IsAdmin
        if self.request.method == 'GET':
            return [IsPsicologo()]
        return [IsAdmin()]

    def get_object(self):
        # El aislamiento garantiza que nunca verá o mutará un clinica_id ajeno
        return self.request.user.clinica

    def perform_update(self, serializer):
        clinica = serializer.save()
        logger.info(
            "TENANT: Clínica '%s' (ID %s) actualizada por %s",
            clinica.nombre,
            clinica.id,
            self.request.user.username,
        )


class UsuarioListCreateAPIView(generics.ListCreateAPIView):
    """[SPRINT 1 - T017] [CU-05] CRUD de psicólogos."""

    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        # [RF-29] Asegurar listar solo personal de la misma clinica del ADMIN
        # Excluimos a los pacientes ya que ellos tienen su propia gestión (T014)
        return (
            Usuario.objects.filter(clinica=self.request.user.clinica)
            .exclude(rol="PACIENTE")
            .order_by("-id")
        )

    def perform_create(self, serializer):
        # Aseguramos que la clínica coincida con la del admin que lo crea
        user = serializer.save(clinica=self.request.user.clinica)
        logger.info(
            "ADMIN: Nuevo psicólogo %s creado por %s",
            user.username,
            self.request.user.username,
        )


class UsuarioDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """[SPRINT 1 - T017] [CU-05] Actualización y eliminación de psicólogos."""

    serializer_class = UsuarioSerializer
    permission_classes = [IsAdmin]

    def get_queryset(self):
        # [RF-29] Aislar a solo los usuarios de la clínica del admin logueado
        return Usuario.objects.filter(clinica=self.request.user.clinica).exclude(
            rol="PACIENTE"
        )

    def perform_update(self, serializer):
        user = serializer.save()
        logger.info(
            "ADMIN: Psicólogo %s actualizado por %s",
            user.username,
            self.request.user.username,
        )

    def perform_destroy(self, instance):
        username = instance.username
        instance.delete()
        logger.info(
            "ADMIN: Psicólogo %s ELIMINADO por %s",
            username,
            self.request.user.username,
        )
