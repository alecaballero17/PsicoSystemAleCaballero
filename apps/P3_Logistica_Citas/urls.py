from django.urls import path

from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateAPIView,
)

urlpatterns = [
    path("api/citas/", CitaListCreateAPIView.as_view(), name="api_citas"),
    path(
        "api/citas/<int:pk>/",
        CitaRetrieveUpdateAPIView.as_view(),
        name="api_citas_detalle",
    ),
]
