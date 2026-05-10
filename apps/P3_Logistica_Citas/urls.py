from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateDestroyAPIView,
    ListaEsperaViewSet,
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
    path("api/", include(router.urls)),
]
