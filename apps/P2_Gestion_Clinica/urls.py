from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    PacienteListCreateAPIView,
    PacienteRetrieveUpdateAPIView,
    HistoriaClinicaViewSet,
    EvolucionClinicaViewSet
)

router = SimpleRouter()
router.register(r'historias', HistoriaClinicaViewSet, basename='historia')
router.register(r'evoluciones', EvolucionClinicaViewSet, basename='evolucion')

urlpatterns = [
    path("api/pacientes/", PacienteListCreateAPIView.as_view(), name="api_pacientes"),
    path(
        "api/pacientes/<int:pk>/",
        PacienteRetrieveUpdateAPIView.as_view(),
        name="api_pacientes_detalle",
    ),
    path("api/", include(router.urls)),
]
