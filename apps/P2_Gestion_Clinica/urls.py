from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PacienteListCreateAPIView,
    PacienteRetrieveUpdateAPIView,
    PacienteSearchAPIView,
    ExpedienteClinicoViewSet,
    NotaClinicaViewSet,
    ArchivoAdjuntoViewSet,
    EvolucionViewSet,
    DiagnosticoPacienteViewSet,
    HistorialCompletoAPIView,
    AnaliticaClinicaAPIView,
    PacienteRegistroPublicoAPIView,
    AssociateClinicAPIView,
)

router = DefaultRouter()
router.register(r'expedientes', ExpedienteClinicoViewSet, basename='expediente')
router.register(r'notas-clinicas', NotaClinicaViewSet, basename='nota-clinica')
router.register(r'archivos-adjuntos', ArchivoAdjuntoViewSet, basename='archivo-adjunto')
# Sprint 4: Evoluciones y Diagnósticos (CU29)
router.register(r'evoluciones', EvolucionViewSet, basename='evolucion')
router.register(r'diagnosticos', DiagnosticoPacienteViewSet, basename='diagnostico-paciente')

urlpatterns = [
    path("api/pacientes/", PacienteListCreateAPIView.as_view(), name="api_pacientes"),
    path(
        "api/pacientes/<int:pk>/",
        PacienteRetrieveUpdateAPIView.as_view(),
        name="api_pacientes_detalle",
    ),
    path("api/pacientes/buscar/", PacienteSearchAPIView.as_view(), name="api_pacientes_buscar"),
    # Sprint 4: Historial completo y Analítica Clínica
    path("api/pacientes/<int:paciente_id>/historial/", HistorialCompletoAPIView.as_view(), name="api_historial_completo"),
    path("api/analitica-clinica/", AnaliticaClinicaAPIView.as_view(), name="api_analitica_clinica"),
    
    # Endpoints Móviles Públicos
    path("api/pacientes/registro-publico/", PacienteRegistroPublicoAPIView.as_view(), name="api_pacientes_registro_publico"),
    path("api/pacientes/me/associate_clinic/", AssociateClinicAPIView.as_view(), name="api_paciente_associate_clinic"),

    path("api/clinica/", include(router.urls)),
]
