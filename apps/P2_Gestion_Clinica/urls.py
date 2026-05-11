from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PacienteListCreateAPIView,
    PacienteRetrieveUpdateAPIView,
    PacienteSearchAPIView,
    ExpedienteClinicoViewSet,
    NotaClinicaViewSet,
    ArchivoAdjuntoViewSet,
)

router = DefaultRouter()
router.register(r'expedientes', ExpedienteClinicoViewSet, basename='expediente')
router.register(r'notas-clinicas', NotaClinicaViewSet, basename='nota-clinica')
router.register(r'archivos-adjuntos', ArchivoAdjuntoViewSet, basename='archivo-adjunto')

urlpatterns = [
    path("api/pacientes/", PacienteListCreateAPIView.as_view(), name="api_pacientes"),
    path(
        "api/pacientes/<int:pk>/",
        PacienteRetrieveUpdateAPIView.as_view(),
        name="api_pacientes_detalle",
    ),
    path("api/pacientes/buscar/", PacienteSearchAPIView.as_view(), name="api_pacientes_buscar"),
    path("api/clinica/", include(router.urls)),
]
