from django.urls import path
from .views import DashboardAPIView, LogAuditoriaAPIView, PredictiveDiagnosisAPIView, TransaccionListCreateAPIView, DescargarComprobantePDFAPIView, VoiceQueryAPIView, BackupDatabaseAPIView, ReporteGeneralPDFAPIView, RestoreDatabaseAPIView, DestruccionControladaAPIView

urlpatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/admin/auditoria/", LogAuditoriaAPIView.as_view(), name="api_admin_auditoria"),
    # Sprint 2: Diagnóstico Predictivo con IA (Gemini)
    path('api/ia/diagnostico/', PredictiveDiagnosisAPIView.as_view(), name='ia_diagnostico'),
    path('api/finanzas/transacciones/', TransaccionListCreateAPIView.as_view(), name='transacciones_list_create'),
    path('api/finanzas/transacciones/<int:transaccion_id>/pdf/', DescargarComprobantePDFAPIView.as_view(), name='descargar_recibo_pdf'),
    path('api/ia/voz-reporte/', VoiceQueryAPIView.as_view(), name='ia_voz_reporte'),
    path('api/ia/backup/', BackupDatabaseAPIView.as_view(), name='ia_backup'),
    path('api/ia/reporte-pdf/', ReporteGeneralPDFAPIView.as_view(), name='ia_reporte_pdf'),
    path('api/ia/restore/', RestoreDatabaseAPIView.as_view(), name='ia_restore'),
    path('api/ia/panic-button/', DestruccionControladaAPIView.as_view(), name='panic-button'),
]
