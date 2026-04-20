from django.urls import path
from .views import DashboardAPIView, LogAuditoriaAPIView

urlpatterns = [
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/admin/auditoria/", LogAuditoriaAPIView.as_view(), name="api_admin_auditoria"),
]
