"""
Configuración de URLs y enrutador principal de PsicoSystem SI2.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


@api_view(["GET"])
@permission_classes([AllowAny])
def api_root(request):
    return Response({"status": "ok", "message": "PsicoSystem API v1"})


def health_check(request):
    """Minimal liveness probe — no auth, no DB, no DRF stack."""
    return JsonResponse({"status": "ok"})


def health_db(request):
    """Database connectivity probe — no auth required."""
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        return JsonResponse({"status": "ok", "database": "reachable"})
    except Exception as exc:
        return JsonResponse(
            {"status": "error", "database": "unreachable", "detail": str(exc)},
            status=503,
        )


urlpatterns = [
    # ── Diagnostic endpoints (registered first, minimal dependencies) ──────
    path("health/", health_check, name="health_check"),
    path("health/db/", health_db, name="health_db"),

    path("", api_root, name="api_root"),
    path("admin/", admin.site.urls),

    # Paquetes de la arquitectura
    path("", include("apps.P1_Identidad_Acceso.urls")),
    path("", include("apps.P2_Gestion_Clinica.urls")),
    path("", include("apps.P3_Logistica_Citas.urls")),
    path("", include("apps.P4_IA_Administracion.urls")),

    # Documentación Profesional (Swagger/Redoc)
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
