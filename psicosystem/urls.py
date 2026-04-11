"""
Configuración de URLs y enrutador principal de PsicoSystem SI2.
"""

from django.contrib import admin
from django.urls import path

# Componentes para Seguridad Stateless (Sprint 1)
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# ✅ 1. Importación de controladores de LÓGICA DE NEGOCIO (core/views)
from core.views import (
    DashboardAPIView,  # T008: Arquitectura de Servicios
    PacienteCreateAPIView,
    PacienteListAPIView,  # <--- NUEVO: Para alimentar la tabla de React
    ClinicaCreateAPIView,
    UsuarioCreateAPIView,
)

# ✅ 2. Importación de controladores de SEGURIDAD (core/security)
from core.security import (
    CustomTokenObtainPairView,
    LogoutAPIView,
    MeAPIView,
)

# ==============================================================================
# ESTRUCTURA DE RUTAS Y MAPEO DE REQUERIMIENTOS
# ==============================================================================
urlpatterns = [
    # --------------------------------------------------------------------------
    # MÓDULO: ADMINISTRACIÓN Y AUTENTICACIÓN (SPRINT 0)
    # --------------------------------------------------------------------------
    path("admin/", admin.site.urls),
    # NOTA DE INGENIERÍA: Las rutas "login/" y "logout/" de Django MVC fueron removidas
    # para consolidar la Arquitectura Híbrida hacia una Pure REST (Causa Raíz #5).
    # T009: DOCUMENTACIÓN API (OpenAPI 3)
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/swagger/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/docs/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
    # --------------------------------------------------------------------------
    # MÓDULO: CAPA API REST (RESOLUCIÓN INCUMPLIMIENTO #1 Y #3)
    # --------------------------------------------------------------------------
    # RF-01 (Autenticación JWT) | T011: Seguridad stateless.
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", LogoutAPIView.as_view(), name="api_logout"),
    path("api/auth/me/", MeAPIView.as_view(), name="api_me"),
    # Servicios de Escritura (Registro vía JSON)
    path("api/clinicas/", ClinicaCreateAPIView.as_view(), name="api_registrar_clinica"),
    path("api/usuarios/", UsuarioCreateAPIView.as_view(), name="api_registrar_usuario"),
    # --- SECCIÓN CRÍTICA PARA REACT ---
    # T008: Dashboard JSON (Métricas)
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    # T014: LISTAR PACIENTES (Este es el que llama tu tabla de React con axios.get)
    path("api/pacientes/", PacienteListAPIView.as_view(), name="api_pacientes_list"),
    # T014: CREAR PACIENTES (Para el formulario de registro vía API)
    path(
        "api/pacientes/registrar/",
        PacienteCreateAPIView.as_view(),
        name="api_pacientes_create",
    ),
]
