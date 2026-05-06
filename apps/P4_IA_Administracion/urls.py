from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    DashboardAPIView, 
    LogAuditoriaAPIView, 
    AnalisisIAView,
    TransaccionViewSet,
    SaldoPacienteView,
    GenerarComprobantePDFView
)

router = DefaultRouter()
router.register(r'transacciones', TransaccionViewSet, basename='transaccion')

urlpatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/admin/auditoria/", LogAuditoriaAPIView.as_view(), name="api_admin_auditoria"),
    path("api/ia/analizar/<int:evolucion_id>/", AnalisisIAView.as_view(), name="api_ia_analizar"),
    
    # Finanzas
    path("api/finanzas/", include(router.urls)),
    path("api/finanzas/saldo/<int:paciente_id>/", SaldoPacienteView.as_view(), name="api_saldo_paciente"),
    path("api/finanzas/comprobante/<int:transaccion_id>/pdf/", GenerarComprobantePDFView.as_view(), name="api_comprobante_pdf"),
]
