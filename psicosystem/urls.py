"""
Configuración de URLs y enrutador principal de PsicoSystem SI2.
"""
from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

# Componentes para Seguridad Stateless (Sprint 1)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

# Importación de controladores de lógica de negocio y API
from core.views import (
    registrar_clinica_view,
    registrar_usuario_view,
    registrar_paciente_view,
    dashboard_view,  # T007: Implementación de UI
    DashboardAPIView,  # T008: Arquitectura de Servicios
    PacienteCreateAPIView,  # T014: Desarrollo de Funcionalidades
    # AÑADIMOS ESTAS DOS:
    ClinicaCreateAPIView,
    UsuarioCreateAPIView,
)

# ==============================================================================
# ESTRUCTURA DE RUTAS Y MAPEO DE REQUERIMIENTOS
# ==============================================================================
urlpatterns = [
    # --------------------------------------------------------------------------
    # MÓDULO: ADMINISTRACIÓN Y AUTENTICACIÓN (SPRINT 0)
    # --------------------------------------------------------------------------
    # T004: Gestión de persistencia de datos maestros mediante ORM.
    path("admin/", admin.site.urls),
    # CU-01 (Iniciar Sesión) | RNF-03 (Seguridad de Acceso) | SPRINT 0
    # Provee el punto de entrada principal al sistema web.
    path(
        "login/",
        auth_views.LoginView.as_view(template_name="core/login.html"),
        name="login",
    ),
    # Gestión de ciclo de vida de sesión (Seguridad RNF-03).
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    # --------------------------------------------------------------------------
    # MÓDULO: PROTOTIPO DE INTERFAZ (T007 | SPRINT 0)
    # --------------------------------------------------------------------------
    # T007: Visualización de Dashboard básico con KPIs para el Psicólogo.
    # Demuestra la integración exitosa del Backend con el Frontend (Bootstrap).
    path("dashboard/", dashboard_view, name="dashboard"),
    # --------------------------------------------------------------------------
    # MÓDULO: CASOS DE USO WEB (MODELO MVC | SPRINT 0 - 1)
    # --------------------------------------------------------------------------
    # CU-25 (Registrar Clínica) | RF-29 (Arquitectura Multi-tenant).
    path("registro-clinica/", registrar_clinica_view, name="registrar_clinica"),
    # CU-02 (Registrar Usuario/Psicólogo) | RF-28 (Gestión de Roles).
    path("registro-psicologo/", registrar_usuario_view, name="registrar_psicologo"),
    # RF-02 (Gestión Pacientes) | RF-29 (Aislamiento de Datos) | SPRINT 1
    # Implementa la lógica de asignación automática de Clínica al Paciente.
    path("registro-paciente/", registrar_paciente_view, name="registrar_paciente"),
    # --------------------------------------------------------------------------
    # MÓDULO: CAPA API REST (RESOLUCIÓN INCUMPLIMIENTO #1 Y #3)
    # --------------------------------------------------------------------------
    # RF-01 (Autenticación JWT) | T011: Seguridad stateless.
    # Autenticación Oficial para React/Flutter
    path("api/auth/login/", TokenObtainPairView.as_view(), name="api_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Servicios de Escritura (Resolución Incumplimiento #3 - Arquitectura Híbrida)
    # Permiten el registro desde clientes externos sin usar el render de Django.
    path("api/clinicas/", ClinicaCreateAPIView.as_view(), name="api_registrar_clinica"),
    path("api/usuarios/", UsuarioCreateAPIView.as_view(), name="api_registrar_usuario"),
    # Servicios de Negocio y Consulta (T008 y T014)
    # T008: Dashboard JSON | T014: Registro de Pacientes con Serializer validado.
    path("api/dashboard/", DashboardAPIView.as_view(), name="api_dashboard"),
    path("api/pacientes/", PacienteCreateAPIView.as_view(), name="api_pacientes"),
]
