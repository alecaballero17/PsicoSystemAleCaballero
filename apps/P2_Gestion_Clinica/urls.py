from django.urls import path

from .views import (
    PacienteListCreateAPIView,
    PacienteRetrieveUpdateAPIView,
)

urlpatterns = [
    path("api/pacientes/", PacienteListCreateAPIView.as_view(), name="api_pacientes"),
    path(
        "api/pacientes/<int:pk>/",
        PacienteRetrieveUpdateAPIView.as_view(),
        name="api_pacientes_detalle",
    ),
]
