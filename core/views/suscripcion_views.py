"""
[SPRINT 1 - T025] Gestión de Suscripciones SaaS: Endpoints de planes y ciclo de vida.
[CU-24] Gestión de Planes y Suscripciones SaaS.
[RF-29] Aislamiento SaaS: Las suscripciones están vinculadas 1:1 a cada Tenant.
[RF-28] Control de Acceso RBAC: Solo administradores gestionan suscripciones.
[RNF-06] Escalabilidad: Arquitectura preparada para soportar múltiples planes concurrentes.
"""
import logging

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.serializers import ModelSerializer, ValidationError

from core.models import PlanSuscripcion, Suscripcion, Clinica
from core.security.permissions import IsAdmin

logger = logging.getLogger(__name__)


# ==============================================================================
# SERIALIZADORES INTERNOS (T025 — Cohesión máxima: vistas + serializadores juntos)
# ==============================================================================

class PlanSuscripcionSerializer(ModelSerializer):
    """[SPRINT 1 - T025] [CU-24] Representación de un plan SaaS."""

    class Meta:
        model = PlanSuscripcion
        fields = [
            "id", "nombre", "descripcion",
            "max_pacientes", "max_psicologos",
            "precio_mensual", "activo",
        ]
        read_only_fields = ["id"]


class SuscripcionSerializer(ModelSerializer):
    """[SPRINT 1 - T025] [CU-24] Representación del estado de suscripción de una clínica."""

    # Campos de solo lectura para la respuesta enriquecida
    clinica_nombre = __import__('rest_framework').serializers.CharField(
        source="clinica.nombre", read_only=True
    )
    plan_nombre = __import__('rest_framework').serializers.CharField(
        source="plan.nombre", read_only=True
    )

    class Meta:
        model = Suscripcion
        fields = [
            "id", "clinica", "clinica_nombre",
            "plan", "plan_nombre",
            "estado", "fecha_inicio", "fecha_fin",
        ]
        read_only_fields = ["id", "clinica_nombre", "plan_nombre", "fecha_inicio"]


# ==============================================================================
# CAPA API: PLANES DE SUSCRIPCIÓN [SPRINT 1 - T025] [CU-24]
# ==============================================================================

class PlanListAPIView(APIView):
    """
    [SPRINT 1 - T025] [CU-24] Lista todos los planes de suscripción activos.
    Endpoint público: permite ver el catálogo sin autenticación.
    """
    # [FIX] Sin authentication_classes, SessionAuthentication rechazaba
    # cookies expiradas con 401 ANTES de evaluar AllowAny en permisos.
    authentication_classes = []

    def get_permissions(self):
        from rest_framework.permissions import AllowAny
        if self.request.method == 'GET':
            return [AllowAny()]
        return [IsAdmin()]  # Solo Administradores pueden crear nuevos planes

    def get(self, request):
        """Retorna el catálogo de planes activos disponibles."""
        planes = PlanSuscripcion.objects.filter(activo=True).order_by("precio_mensual")  # pylint: disable=no-member
        serializer = PlanSuscripcionSerializer(planes, many=True)
        logger.info("SAAS: Consulta pública del catálogo de planes.")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Crea un nuevo plan de suscripción en el catálogo."""
        serializer = PlanSuscripcionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            logger.info(
                "SAAS: Admin %s creó el plan '%s'.",
                request.user.username,
                request.data.get("nombre"),
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# CAPA API: GESTIÓN DE SUSCRIPCIONES POR CLÍNICA [SPRINT 1 - T025] [CU-24]
# ==============================================================================

class SuscripcionClinicaAPIView(APIView):
    """
    [SPRINT 1 - T025] [CU-24] [RF-29] Gestiona la suscripción de una clínica específica.
    GET  /api/suscripciones/<clinica_id>/  → Detalle del estado de suscripción
    PUT  /api/suscripciones/<clinica_id>/  → Cambio de plan o estado
    """

    permission_classes = [IsAdmin]  # [RF-28] [RF-29] Solo ADMIN gestiona suscripciones

    def _get_suscripcion(self, clinica_id):
        """Helper: obtiene la suscripción asociada a la clínica o None."""
        try:
            clinica = Clinica.objects.get(pk=clinica_id)  # pylint: disable=no-member
            suscripcion = clinica.suscripcion
            return clinica, suscripcion
        except Clinica.DoesNotExist:  # pylint: disable=no-member
            return None, None
        except Suscripcion.DoesNotExist:  # pylint: disable=no-member
            return clinica, None

    def get(self, request, clinica_id):
        """[T025] Detalle del estado de suscripción de una clínica (Tenant)."""
        clinica, suscripcion = self._get_suscripcion(clinica_id)

        if clinica is None:
            return Response(
                {"error": "Clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if suscripcion is None:
            # Clínica sin suscripción aún
            return Response(
                {
                    "clinica_id": clinica_id,
                    "clinica_nombre": clinica.nombre,
                    "estado": "SIN_SUSCRIPCION",
                    "mensaje": "Esta clínica aún no tiene un plan asignado.",
                },
                status=status.HTTP_200_OK,
            )

        # [RF-29] Verificación de límites de uso por suscripción
        from core.models import Paciente, Usuario  # import local para evitar circularidad
        total_pacientes = Paciente.objects.filter(clinica=clinica).count()  # pylint: disable=no-member
        total_psicologos = Usuario.objects.filter(  # pylint: disable=no-member
            clinica=clinica, rol="PSICOLOGO"
        ).count()

        serializer = SuscripcionSerializer(suscripcion)
        data = serializer.data
        data["uso"] = {
            "pacientes_actuales": total_pacientes,
            "pacientes_limite": suscripcion.plan.max_pacientes,
            "psicologos_actuales": total_psicologos,
            "psicologos_limite": suscripcion.plan.max_psicologos,
            "pacientes_disponibles": (
                suscripcion.plan.max_pacientes - total_pacientes
            ),
        }

        logger.info(
            "SAAS: Consulta de suscripción de Clínica ID %s por Admin %s.",
            clinica_id,
            request.user.username,
        )
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request, clinica_id):
        """[T025] Cambia el plan o el estado de la suscripción de una clínica."""
        clinica, suscripcion = self._get_suscripcion(clinica_id)

        if clinica is None:
            return Response(
                {"error": "Clínica no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if suscripcion is None:
            # Crear suscripción si no existe (alta inicial de plan)
            serializer = SuscripcionSerializer(data={**request.data, "clinica": clinica_id})
        else:
            # Actualizar suscripción existente (cambio de plan o estado)
            serializer = SuscripcionSerializer(suscripcion, data=request.data, partial=True)

        if serializer.is_valid():
            instancia = serializer.save()
            logger.info(
                "SAAS: Admin %s actualizó suscripción de Clínica ID %s → Plan: %s / Estado: %s",
                request.user.username,
                clinica_id,
                instancia.plan.nombre,
                instancia.estado,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ==============================================================================
# CAPA API: VERIFICADOR DE LÍMITES [SPRINT 1 - T025] [RF-29]
# ==============================================================================

class LimitesClinicaAPIView(APIView):
    """
    [SPRINT 1 - T025] [RF-29] Verifica si una clínica ha alcanzado los límites de su plan.
    Utilizable como guard en el flujo de creación de pacientes y psicólogos.
    GET /api/suscripciones/<clinica_id>/limites/
    """

    permission_classes = [IsAdmin]

    def get(self, request, clinica_id):
        """Retorna el estado de los límites de uso de la clínica."""
        try:
            clinica = Clinica.objects.get(pk=clinica_id)  # pylint: disable=no-member
            suscripcion = clinica.suscripcion
        except (Clinica.DoesNotExist, Suscripcion.DoesNotExist):  # pylint: disable=no-member
            return Response(
                {"error": "Clínica o suscripción no encontrada."},
                status=status.HTTP_404_NOT_FOUND,
            )

        from core.models import Paciente, Usuario  # import local
        total_pacientes = Paciente.objects.filter(clinica=clinica).count()  # pylint: disable=no-member
        total_psicologos = Usuario.objects.filter(  # pylint: disable=no-member
            clinica=clinica, rol="PSICOLOGO"
        ).count()

        limite_alcanzado_pacientes = total_pacientes >= suscripcion.plan.max_pacientes
        limite_alcanzado_psicologos = total_psicologos >= suscripcion.plan.max_psicologos

        return Response(
            {
                "clinica": clinica.nombre,
                "plan": suscripcion.plan.nombre,
                "estado_suscripcion": suscripcion.estado,
                "suscripcion_activa": suscripcion.esta_activa(),
                "limites": {
                    "pacientes": {
                        "actual": total_pacientes,
                        "maximo": suscripcion.plan.max_pacientes,
                        "limite_alcanzado": limite_alcanzado_pacientes,
                    },
                    "psicologos": {
                        "actual": total_psicologos,
                        "maximo": suscripcion.plan.max_psicologos,
                        "limite_alcanzado": limite_alcanzado_psicologos,
                    },
                },
            },
            status=status.HTTP_200_OK,
        )
