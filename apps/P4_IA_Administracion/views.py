"""
P4_IA_Administracion — Vistas de Administración, Auditoría e IA Predictiva.
Integración con Google Gemini para diagnóstico asistido por inteligencia artificial.
"""
import logging
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita
from .models import LogAuditoria, DiagnosticoIA, Transaccion, Comprobante
from .serializers import TransaccionSerializer, ComprobanteSerializer

logger = logging.getLogger(__name__)


# ==============================================================================
# Auditoría (Sprint 1)
# ==============================================================================
class LogAuditoriaAPIView(APIView):
    """
    Endpoint de bitácora exclusivo para el Administrador de la clínica.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def get(self, request):
        clinica = request.user.clinica
        logs = LogAuditoria.objects.filter(usuario__clinica=clinica).order_by('-fecha')[:50]
        
        data = [
            {
                "fecha": log.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": getattr(log.usuario, "username", "Desconocido") if log.usuario else "Desconocido",
                "accion": log.accion
            }
            for log in logs
        ]
        return Response(data, status=status.HTTP_200_OK)


# ==============================================================================
# Dashboard (Sprint 1)
# ==============================================================================
class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get(self, request):
        clinica = request.user.clinica
        total_pacientes = Paciente.objects.filter(clinica=clinica).count() if clinica else 0
        citas_pendientes = Cita.objects.filter(
            paciente__clinica=clinica, estado="PENDIENTE"
        ).count() if clinica else 0

        data = {
            "clinica": clinica.nombre if clinica else "Sin Clínica",
            "metricas": {
                "total_pacientes": total_pacientes,
                "citas_pendientes": citas_pendientes,
            },
        }
        return Response(data, status=status.HTTP_200_OK)


# ==============================================================================
# IA: Diagnóstico Predictivo con Google Gemini (Sprint 2)
# ==============================================================================
def _get_gemini_client():
    """Inicializa el cliente de Gemini con la API Key del entorno."""
    from decouple import config as decouple_config
    api_key = decouple_config("GEMINI_API_KEY", default="")
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_name = "gemini-flash-latest"
        return genai.GenerativeModel(model_name)
    except Exception as e:
        logger.error("Error al inicializar Gemini: %s", e)
        return None


SYSTEM_PROMPT_PSICOLOGIA = """Eres un asistente de inteligencia artificial especializado en psicología clínica. 
Tu rol es APOYAR al profesional de salud mental analizando notas clínicas y sugiriendo posibles 
líneas de evaluación diagnóstica basándote en el DSM-5-TR y CIE-11.

REGLAS ESTRICTAS:
1. NUNCA emitas un diagnóstico definitivo. Siempre usa lenguaje probabilístico ("sugiere", "podría indicar", "es compatible con").
2. SIEMPRE recomienda que el profesional realice la evaluación clínica completa.
3. Estructura tu respuesta en: a) Análisis de síntomas identificados, b) Diagnósticos diferenciales sugeridos, c) Recomendaciones de evaluación adicional.
4. Responde en español.
5. Sé conciso y profesional. Máximo 500 palabras.
"""


class PredictiveDiagnosisAPIView(APIView):
    """
    POST: Envía notas clínicas de un paciente a Google Gemini para obtener
    un análisis de diagnóstico predictivo asistido por IA.
    
    Requiere: Token JWT, rol PSICOLOGO/ADMIN, clínica asignada.
    Body: { "paciente_id": int, "notas": "texto de notas clínicas" }
    """
    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador, HasClinicaAsignada]

    def post(self, request):
        notas = request.data.get('notas', '').strip()
        paciente_id = request.data.get('paciente_id', None)

        # Validar input
        if not notas:
            return Response(
                {"detail": "El campo 'notas' es obligatorio y no puede estar vacío."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(notas) < 20:
            return Response(
                {"detail": "Las notas clínicas deben tener al menos 20 caracteres para un análisis significativo."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Validar que el paciente pertenece a la clínica del usuario
        paciente = None
        if paciente_id:
            try:
                paciente = Paciente.objects.get(
                    pk=paciente_id,
                    clinica=request.user.clinica,
                )
            except Paciente.DoesNotExist:
                return Response(
                    {"detail": "Paciente no encontrado o no pertenece a tu clínica."},
                    status=status.HTTP_404_NOT_FOUND,
                )

        # Intentar llamar a Gemini
        model = _get_gemini_client()
        if model is None:
            return Response(
                {
                    "detail": "El servicio de IA no está configurado. Contacte al administrador para configurar la GEMINI_API_KEY.",
                    "diagnostico_ia": None,
                    "fuente": "sin_configurar",
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            prompt = f"{SYSTEM_PROMPT_PSICOLOGIA}\n\n--- NOTAS CLÍNICAS DEL PACIENTE ---\n{notas}\n--- FIN DE NOTAS ---"
            response = model.generate_content(prompt)
            resultado_ia = response.text
            fuente = "gemini-flash-latest"
        except Exception as e:
            logger.error("Error en llamada a Gemini: %s", e)
            return Response(
                {
                    "detail": f"Error al comunicarse con el servicio de IA: {str(e)}",
                    "diagnostico_ia": None,
                    "fuente": "error",
                },
                status=status.HTTP_502_BAD_GATEWAY,
            )

        # Persistir el diagnóstico en la base de datos
        diagnostico = DiagnosticoIA.objects.create(
            paciente=paciente,
            psicologo=request.user,
            input_clinico=notas,
            resultado_ia=resultado_ia,
            probabilidad_acierto=0.0,  # Gemini no devuelve probabilidad numérica
        )

        # Registrar en auditoría
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Solicitó diagnóstico IA para paciente ID={paciente_id or 'N/A'} (Diagnóstico #{diagnostico.pk})",
        )

        return Response(
            {
                "diagnostico_id": diagnostico.pk,
                "diagnostico_ia": resultado_ia,
                "fuente": fuente,
                "paciente_id": paciente_id,
                "fecha_analisis": diagnostico.fecha_analisis.strftime("%Y-%m-%d %H:%M:%S"),
            },
            status=status.HTTP_200_OK,
        )

    def get(self, request):
        """GET: Listar historial de diagnósticos IA de la clínica."""
        diagnosticos = DiagnosticoIA.objects.filter(
            psicologo__clinica=request.user.clinica,
        ).select_related("paciente", "psicologo").order_by("-fecha_analisis")[:20]

        data = [
            {
                "id": d.pk,
                "paciente": d.paciente.nombre if d.paciente else "N/A",
                "psicologo": d.psicologo.username,
                "input_clinico": d.input_clinico[:100] + "..." if len(d.input_clinico) > 100 else d.input_clinico,
                "resultado_ia": d.resultado_ia[:200] + "..." if len(d.resultado_ia) > 200 else d.resultado_ia,
                "fecha_analisis": d.fecha_analisis.strftime("%Y-%m-%d %H:%M:%S"),
            }
            for d in diagnosticos
        ]
        return Response(data, status=status.HTTP_200_OK)


# ==============================================================================
# Módulo Financiero (CU11/CU12)
# ==============================================================================
class TransaccionListCreateAPIView(APIView):
    """
    Listar y crear transacciones (pagos) para pacientes.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador]

    def get(self, request):
        transacciones = Transaccion.objects.filter(clinica=request.user.clinica).order_by('-fecha')
        serializer = TransaccionSerializer(transacciones, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransaccionSerializer(data=request.data)
        if serializer.is_valid():
            # Crear la transacción vinculada a la clínica del usuario
            transaccion = serializer.save(clinica=request.user.clinica)
            
            # Generar comprobante automático (Simplificado para el Sprint 2)
            import uuid
            nro = f"REC-{uuid.uuid4().hex[:8].upper()}"
            comprobante = Comprobante.objects.create(
                transaccion=transaccion,
                nro_comprobante=nro
            )
            
            # Auditoría
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=f"Registró pago de {transaccion.monto} BS del paciente {transaccion.paciente.nombre}"
            )
            
            return Response({
                "id": transaccion.id,
                "nro_comprobante": comprobante.nro_comprobante,
                "mensaje": "Pago registrado y comprobante generado."
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
