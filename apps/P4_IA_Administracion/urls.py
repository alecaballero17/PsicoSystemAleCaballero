from django.urls import path
from .views import DashboardAPIView, LogAuditoriaAPIView, PredictiveDiagnosisAPIView, TransaccionListCreateAPIView

urlpatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/admin/auditoria/", LogAuditoriaAPIView.as_view(), name="api_admin_auditoria"),
    # Sprint 2: Diagnóstico Predictivo con IA (Gemini)
    path('api/ia/diagnostico/', PredictiveDiagnosisAPIView.as_view(), name='ia_diagnostico'),
    path('api/finanzas/transacciones/', TransaccionListCreateAPIView.as_view(), name='transacciones_list_create'),
]
