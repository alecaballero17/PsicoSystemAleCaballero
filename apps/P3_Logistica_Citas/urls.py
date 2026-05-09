from django.urls import path, include
from rest_framework.routers import SimpleRouter

from .views import (
    CitaListCreateAPIView,
    CitaRetrieveUpdateAPIView,
    ListaEsperaViewSet,
)


router = SimpleRouter()
router.register(r'api/lista-espera', ListaEsperaViewSet, basename='lista-espera')

urlpatterns = [
    path('', include(router.urls)),
    path("api/citas/", CitaListCreateAPIView.as_view(), name="api_citas"),
    path(
        "api/citas/<int:pk>/",
        CitaRetrieveUpdateAPIView.as_view(),
        name="api_citas_detalle",
    ),
]

