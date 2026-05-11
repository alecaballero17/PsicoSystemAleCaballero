"""
Configuración de URLs y enrutador principal de PsicoSystem SI2.
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({"status": "ok", "message": "PsicoSystem API v1"})


urlpatterns = [
    path("", api_root, name="api_root"),
    path("admin/", admin.site.urls),

    # Paquetes de la arquitectura
    path("", include("apps.P1_Identidad_Acceso.urls")),
    path("", include("apps.P2_Gestion_Clinica.urls")),
    path("", include("apps.P3_Logistica_Citas.urls")),
    path("", include("apps.P4_IA_Administracion.urls")),

    # Documentación Profesional (Swagger/Redoc)
    from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
