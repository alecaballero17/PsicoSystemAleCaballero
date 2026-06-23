from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateDestroyAPIView,
    ListaEsperaViewSet,
    CitaEnviarRecordatorioAPIView,
    CitaCancelarWebAPIView,
)
from .views_mobile import (
    MobileCitasAPIView,
    MobileCitaCancelarAPIView,
    MobileCitaFichaPDFAPIView,
    MobilePacientePagarAPIView,
    MobileStripeCheckoutAPIView,
    MobileStripeWebhookAPIView,
    MobileCitasDisponibilidadAPIView,
    MobilePsicologosListAPIView,
    MobileRecomendacionesAPIView,
)

# T031: Router para Lista de Espera
router = SimpleRouter()
router.register(r'lista-espera', ListaEsperaViewSet, basename='lista-espera')

urlpatterns = [
    path("api/citas/", CitaListCreateAPIView.as_view(), name="api_citas"),
    path(
        "api/citas/<int:pk>/",
        CitaRetrieveUpdateDestroyAPIView.as_view(),
        name="api_citas_detalle",
    ),
    path("api/citas/<int:pk>/enviar_recordatorio/", CitaEnviarRecordatorioAPIView.as_view(), name="api_citas_recordatorio"),
    path("api/citas/<int:pk>/cancelar/", CitaCancelarWebAPIView.as_view(), name="api_citas_cancelar"),
    path("api/", include(router.urls)),
    
    # Endpoints móviles
    path("api/mobile/citas/", MobileCitasAPIView.as_view(), name="mobile_citas"),
    path("api/mobile/citas/<int:pk>/cancelar/", MobileCitaCancelarAPIView.as_view(), name="mobile_citas_cancelar"),
    path("api/mobile/paciente/pagar/", MobilePacientePagarAPIView.as_view(), name="mobile_paciente_pagar"),
    path("api/mobile/paciente/stripe-checkout/", MobileStripeCheckoutAPIView.as_view(), name="mobile_stripe_checkout"),
    path("api/mobile/stripe/webhook/", MobileStripeWebhookAPIView.as_view(), name="mobile_stripe_webhook"),
    path("api/mobile/citas/<int:cita_id>/pdf/", MobileCitaFichaPDFAPIView.as_view(), name="mobile_citas_pdf"),
    path("api/mobile/psicologos/", MobilePsicologosListAPIView.as_view(), name="mobile_psicologos"),
    path("api/mobile/citas/disponibilidad/", MobileCitasDisponibilidadAPIView.as_view(), name="mobile_disponibilidad"),
    path("api/mobile/recomendaciones/", MobileRecomendacionesAPIView.as_view(), name="mobile_recomendaciones_list"),
    path("api/mobile/recomendaciones/<int:pk>/", MobileRecomendacionesAPIView.as_view(), name="mobile_recomendaciones_update"),
]
