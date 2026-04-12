"""
Configuración de URLs y enrutador principal de PsicoSystem SI2.
[SPRINT 0 - T001] [SPRINT 0 - T009] Arquitectura REST + Documentación OpenAPI.
[SPRINT 1 - T011] [T014] [T017] [T022] [T024] Endpoints de negocio.
"""

from django.contrib import admin
from django.urls import path

# [SPRINT 1 - T011] Componentes para Seguridad Stateless
from rest_framework_simplejwt.views import (
    TokenRefreshView,
)
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

# [SPRINT 0 - T008] [SPRINT 1 - T014] [T024] Importación de controladores de negocio
from core.views import (
    DashboardAPIView,  # [SPRINT 1] Métricas del dashboard
    PacienteCreateAPIView,
    PacienteRegistroPublicoAPIView,
    PacienteListAPIView,  # [SPRINT 1 - T014] Listado de pacientes para React
    PacienteDeleteAPIView,  # [RF-30] Borrado seguro
    AssociateClinicAPIView,  # [RF-29] Nueva vinculación para huérfanos
    ClinicaCreateAPIView,
    ClinicaConfigAPIView,  # [SPRINT 1 - RF-29] Mantenimiento de Tenant
    UsuarioListCreateAPIView,
    UsuarioDetailAPIView,
    PlanListAPIView,  # [SPRINT 1 - T025] Catálogo de planes SaaS
    SuscripcionClinicaAPIView,  # [SPRINT 1 - T025] [CU-24] Gestión por clínica
    LimitesClinicaAPIView,  # [SPRINT 1 - T025] Verificador de límites
)

# [SPRINT 1 - T011] [T018] [T019] [T022] Importación de controladores de seguridad
from core.security import (
    CustomTokenObtainPairView,
    LogoutAPIView,
    MeAPIView,
    PasswordResetRequestAPIView,  # [SPRINT 1 - T019] [T020]
    PasswordResetConfirmAPIView,  # [SPRINT 1 - T019] [T020]
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
    # [SPRINT 1 - T011] [RF-01] [CU-01] Autenticación JWT stateless.
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # [SPRINT 1 - T022] [CU-04]
    path(
        "api/auth/logout/",
        LogoutAPIView.as_view(),
        name="api_logout",
    ),
    # [SPRINT 1 - T011] [RF-03]
    path("api/auth/me/", MeAPIView.as_view(), name="api_me"),
    # [SPRINT 1 - T019] [T020] [CU-03] Recuperación de contraseña
    path(
        "api/auth/password-reset/",
        PasswordResetRequestAPIView.as_view(),
        name="api_password_reset",
    ),
    path(
        "api/auth/password-reset/confirm/",
        PasswordResetConfirmAPIView.as_view(),
        name="api_password_reset_confirm",
    ),
    # [SPRINT 1 - T024] [CU-25] Registro de clínicas B2B y Mantenimiento de Tenant (RF-29)
    path("api/clinicas/", ClinicaCreateAPIView.as_view(), name="api_registrar_clinica"),
    path(
        "api/clinica/me/", ClinicaConfigAPIView.as_view(), name="api_config_clinica_me"
    ),
    # [SPRINT 1 - T017] [RF-04] Registro y gestión de psicólogos (CRUD completo)
    path(
        "api/usuarios/",
        UsuarioListCreateAPIView.as_view(),
        name="api_usuarios_list_create",
    ),
    path(
        "api/usuarios/<int:pk>/",
        UsuarioDetailAPIView.as_view(),
        name="api_usuarios_detail",
    ),
    # --- SECCIÓN CRÍTICA PARA REACT ---
    # [SPRINT 1] Dashboard JSON (Métricas)
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    # T014: LISTAR PACIENTES (Este es el que llama tu tabla de React con axios.get)
    path("api/pacientes/", PacienteListAPIView.as_view(), name="api_pacientes_list"),
    # T014: CREAR PACIENTES (Para el formulario de registro vía API)
    path(
        "api/pacientes/registrar/",
        PacienteCreateAPIView.as_view(),
        name="api_pacientes_create",
    ),
    path(
        "api/pacientes/<int:pk>/",
        PacienteDeleteAPIView.as_view(),
        name="api_pacientes_delete",
    ),
    # [ALINEACIÓN SPRINT 1 - RF-29] Vinculación post-login para usuarios huérfanos en Flutter
    path(
        "api/pacientes/me/associate_clinic/",
        AssociateClinicAPIView.as_view(),
        name="api_paciente_associate_clinic",
    ),
    # --------------------------------------------------------------------------
    # [SPRINT 1 - T025] [CU-24] SUSCRIPCIONES Y PLANES SaaS
    # --------------------------------------------------------------------------
    path("api/planes/", PlanListAPIView.as_view(), name="api_planes_lista"),
    path(
        "api/suscripciones/<int:clinica_id>/",
        SuscripcionClinicaAPIView.as_view(),
        name="api_suscripcion_clinica",
    ),
    path(
        "api/suscripciones/<int:clinica_id>/limites/",
        LimitesClinicaAPIView.as_view(),
        name="api_suscripcion_limites",
    ),
    # --------------------------------------------------------------------------
    # [SPRINT 1 - T015] AUTOGESTIÓN DE USUARIOS (ONBOARDING)
    # --------------------------------------------------------------------------
    path(
        "api/pacientes/registro-publico/",
        PacienteRegistroPublicoAPIView.as_view(),
        name="api_pacientes_registro_publico",
    ),
]
