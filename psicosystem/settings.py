"""
Configuración principal de PsicoSystem SI2.
"""
from pathlib import Path
from datetime import timedelta
from decouple import config  # RNF-03: Seguridad de credenciales | SPRINT 0

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECCIÓN: SEGURIDAD (RNF-03 | PUNTO 12 AUDITORÍA | SPRINT 0)
# ==============================================================================
# T001: Definición de arquitectura segura.
# Se utiliza 'decouple' para evitar el hardcodeo de llaves, cumpliendo con RNF-03.
SECRET_KEY = config("SECRET_KEY", default="django-insecure-psicosystem-2026-audit-fix")

# T004: Configuración del entorno de desarrollo.
DEBUG = config("DEBUG", default=True, cast=bool)

ALLOWED_HOSTS = []

# ==============================================================================
# SECCIÓN: DEFINICIÓN DE APLICACIONES (T001, T002 | SPRINT 0)
# ==============================================================================
INSTALLED_APPS = [
    "core",  # T003: Estructura de app principal y modelos Multi-tenant.
    "rest_framework",  # T008: Conexión básica para arquitectura REST (API).
    "rest_framework_simplejwt",  # RF-01: Autenticación JWT (Sprint 1 - T011).
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",  # <--- AGREGAR ESTA LÍNEA
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # <--- DEBE IR AQUÍ (PRIMERO O SEGUNDO)
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # RNF-03: Seguridad contra ataques CSRF.
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "psicosystem.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "psicosystem.wsgi.application"

# ==============================================================================
# SECCIÓN: PERSISTENCIA (T004 | INFRAESTRUCTURA POSTGRESQL | SPRINT 0)
# ==============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db_psicosystem",
        "USER": "postgres",
        "PASSWORD": config("DB_PASSWORD"),  # <--- CAMBIO CLAVE: Ya no dice "1234"
        "HOST": "127.0.0.1",
        "PORT": "5432",
    }
}

# ==============================================================================
# SECCIÓN: CONFIGURACIÓN API REST Y JWT (RF-01 | T011 | T008 | SPRINT 1)
# ==============================================================================
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",  # RF-01: Seguridad JWT.
        "rest_framework.authentication.SessionAuthentication",  # T007: Visualización en navegador.
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",  # RNF-03: Restricción de acceso global.
    ),
}

# RF-01: Parámetros del ciclo de vida del Token (Seguridad Stateless).
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# ==============================================================================
# SECCIÓN: GESTIÓN DE IDENTIDAD (RF-28 | ROLES | SPRINT 0)
# ==============================================================================
# T005: Diseño del modelo de usuario extendido para soporte Multi-tenant (RF-29).
AUTH_USER_MODEL = "core.Usuario"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================================================================
# SECCIÓN: LOCALIZACIÓN (ESTÁNDARES BOLIVIA - UAGRM | SPRINT 0)
# ==============================================================================
LANGUAGE_CODE = "es-bo"
TIME_ZONE = "America/La_Paz"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"

# ==============================================================================
# SECCIÓN: REDIRECCIONES DE FLUJO (SOLUCIÓN T007 | SPRINT 0)
# ==============================================================================
# CU-01: Inicio de sesión.
LOGIN_URL = "/login/"
# T007: Cumplimiento del Prototipo UI (Dashboard funcional).
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# Configuración de CORS para Interoperabilidad (RNF)
CORS_ALLOW_ALL_ORIGINS = True  # Permite que cualquier cliente (React/Mobile) se conecte
