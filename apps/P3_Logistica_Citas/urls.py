from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateAPIView,
    CitaViewSet,
    ListaEsperaViewSet,
    MobileCitasDisponibilidadAPIView,
    MobileCitasAPIView,
)

router = DefaultRouter()
router.register(r'gestion', CitaViewSet, basename='cita-gestion')
router.register(r'lista-espera', ListaEsperaViewSet, basename='lista-espera')

urlpatterns = [
    path("api/citas/", CitaListCreateAPIView.as_view(), name="api_citas"),
    path(
        "api/citas/<int:pk>/",
        CitaRetrieveUpdateAPIView.as_view(),
        name="api_citas_detalle",
    ),
    path("api/logistica/", include(router.urls)),
    path("api/mobile/citas/disponibilidad/", MobileCitasDisponibilidadAPIView.as_view(), name="api_mobile_disponibilidad"),
    path("api/mobile/citas/", MobileCitasAPIView.as_view(), name="api_mobile_citas"),
]
