from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateAPIView,
    CitaViewSet,
    ListaEsperaViewSet,
)
from .views_mobile import (
    MobileCitasAPIView,
    MobileCitaCancelarAPIView,
    MobileCitaFichaPDFAPIView,
    MobilePacientePagarAPIView,
    MobileCitasDisponibilidadAPIView,
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
    
    # Endpoints móviles (Flutter App)
    path("api/mobile/citas/", MobileCitasAPIView.as_view(), name="mobile_citas"),
    path("api/mobile/citas/<int:pk>/cancelar/", MobileCitaCancelarAPIView.as_view(), name="mobile_citas_cancelar"),
    path("api/mobile/paciente/pagar/", MobilePacientePagarAPIView.as_view(), name="mobile_paciente_pagar"),
    path("api/mobile/citas/<int:cita_id>/pdf/", MobileCitaFichaPDFAPIView.as_view(), name="mobile_citas_pdf"),
    path("api/mobile/citas/disponibilidad/", MobileCitasDisponibilidadAPIView.as_view(), name="mobile_disponibilidad"),
]
