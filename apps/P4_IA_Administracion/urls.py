from django.urls import path, include
from rest_framework.routers import SimpleRouter
from .views import (
    DashboardAPIView, 
    LogAuditoriaAPIView, 
    AnalisisIAView,
    TransaccionViewSet,
    SaldoPacienteView,
    GenerarComprobantePDFView,
    ReportePersonalizadoAPIView,
    MobileSaldoPacienteView,
    PasarelaPagoMobileAPIView,
    RegistroTokenFCMAPIView,
    VoiceToReportAPIView
)

router = SimpleRouter()
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')

urlpatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/admin/auditoria/", LogAuditoriaAPIView.as_view(), name="api_admin_auditoria"),
    path("api/ia/analizar/<int:evolucion_id>/", AnalisisIAView.as_view(), name="api_ia_analizar"),
    
    # Finanzas
    path("api/finanzas/", include(router.urls)),
    path("api/finanzas/saldo/<int:paciente_id>/", SaldoPacienteView.as_view(), name="api_saldo_paciente"),
    path("api/finanzas/comprobante/<int:transaccion_id>/pdf/", GenerarComprobantePDFView.as_view(), name="api_comprobante_pdf"),
    path("api/reportes/personalizado/", ReportePersonalizadoAPIView.as_view(), name="api_reporte_personalizado"),
    path("api/reportes/voz/", VoiceToReportAPIView.as_view(), name="api_reportes_voz"),

    # Mobile Flutter Endpoints
    path("api/mobile/paciente/<int:paciente_id>/saldo/", MobileSaldoPacienteView.as_view(), name="api_mobile_saldo"),
    path("api/mobile/paciente/pagar/", PasarelaPagoMobileAPIView.as_view(), name="api_mobile_pagar"),
    path("api/mobile/notificaciones/registrar-token/", RegistroTokenFCMAPIView.as_view(), name="api_mobile_fcm_token"),
]
