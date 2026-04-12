"""
Configuración principal de PsicoSystem SI2.
[SPRINT 0 - T001] Arquitectura desacoplada: Este archivo centraliza la configuración
del servidor Backend (Django REST), separado del Frontend (React) y Móvil (Flutter).
[SPRINT 0 - T002] Stack Tecnológico validado: Django + DRF + PostgreSQL + SimpleJWT.
"""

from pathlib import Path
from datetime import timedelta
import os

try:
    import dj_database_url
except ImportError:
    dj_database_url = None
# [SPRINT 0 - T001] [RNF-03] Seguridad de credenciales vía variables de entorno
from decouple import config

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECCIÓN: SEGURIDAD (RNF-03 | PUNTO 12 AUDITORÍA | SPRINT 0)
# ==============================================================================
# [SPRINT 0 - T001] [RNF-03] Definición de arquitectura segura.
# Se utiliza 'decouple' para evitar el hardcodeo de llaves, cumpliendo con RNF-03.
SECRET_KEY = config("SECRET_KEY")  # [RNF-03] Secreto extraído de .env, nunca hardcodeado

# [SPRINT 0 - T004] Configuración del entorno de desarrollo.
DEBUG = config("DEBUG", default=True, cast=bool)  # [SPRINT 0 - T004] Control por entorno

# ==============================================================================
# SECCIÓN: SEGURIDAD DE RED Y HOSTS (RNF-01 | RNF-03 | SPRINT 1)
# ==============================================================================
# Leemos la IP del .env para el día de la defensa (Hotspot/Wi-Fi)
# [SPRINT 0 - T004] [RNF-03] IP configurable por entorno
SERVER_IP = config("SERVER_IP", default="127.0.0.1")

# [SPRINT 0 - T001] [RNF-03] Soporte Servidores Cloud y Desarrollo
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=f"localhost,127.0.0.1,{SERVER_IP},.onrender.com").split(',')

# ==============================================================================
# SECCIÓN: DEFINICIÓN DE APLICACIONES (T001, T002 | SPRINT 0)
# ==============================================================================
INSTALLED_APPS = [
    "corsheaders",  # [SPRINT 0 - T008] [RNF-05] Requerido para la conexión CORS con React y Flutter
    "core",  # [SPRINT 0 - T001] Estructura de app principal y modelos Multi-tenant.
    "rest_framework",  # [SPRINT 0 - T002] [T008] Stack DRF para arquitectura REST (API).
    "rest_framework_simplejwt",  # [ADELANTO SPRINT 1] RF-01: Autenticación JWT (T011).
    "rest_framework_simplejwt.token_blacklist",  # [ADELANTO SPRINT 1] CU-04: Revocación de tokens.
    "drf_spectacular",  # [SPRINT 0 - T009] Documentación de API (OpenAPI 3).
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",  # [SPRINT 0 - T008] [RNF-05] CORS
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # [RENDER] Servir estáticos
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # [RNF-03] CSRF
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "core.security.audit_middleware.AuditLogMiddleware",  # [SPRINT 1 - T023] [RF-30] Auditoría
]

ROOT_URLCONF = "psicosystem.urls"

# ==============================================================================
# CONFIGURACIÓN CORS (INTEROPERABILIDAD REACT/FLUTTER)
# ==============================================================================
# [SPRINT 0 - T008] [RNF-05] Permitir que Flutter (Android/iOS) conecte sin restricciones de origen
# Las Apps móviles no envían el header 'Origin' como los navegadores.
CORS_ALLOW_ALL_ORIGINS = True  # [SPRINT 0 - T008] Seguro porque usamos JWT para validar peticiones

# Configuración de CORS para Interoperabilidad Web (React <-> Django)
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    f"http://{SERVER_IP}:3000",  # Para que React funcione desde la IP de la red local
]

CORS_ALLOW_METHODS = [
    "DELETE",
    "GET",
    "OPTIONS",
    "PATCH",
    "POST",
    "PUT",
]
CORS_ALLOW_HEADERS = [
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrf-token",
    "x-requested-with",
]
CORS_ALLOW_CREDENTIALS = True

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
# SECCIÓN: PERSISTENCIA [SPRINT 0 - T002] [T004] [T005] INFRAESTRUCTURA POSTGRESQL
# ==============================================================================
DATABASES = {
    "default": {
        # [SPRINT 0 - T002] Stack: PostgreSQL seleccionado
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "db_psicosystem",
        "USER": "postgres",
        "PASSWORD": config("DB_PASSWORD", default=""),  # [RNF-03] Extraído de forma segura del .env
        "HOST": "127.0.0.1",  # [SPRINT 0 - T004] Entorno de desarrollo local
        "PORT": "5432",
    }
}

# [RENDER NUBE] Captación nativa de base de datos desde URL si existe
if dj_database_url and config("DATABASE_URL", default=""):
    DATABASES["default"] = dj_database_url.config(
        default=config("DATABASE_URL"),
        conn_max_age=600,
        conn_health_checks=True,
    )

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
    # [SPRINT 0 - T009] Documentación de API
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# T009: Configuración de OpenAPI
SPECTACULAR_SETTINGS = {
    "TITLE": "PsicoSystem SI2 API",
    "DESCRIPTION": "Arquitectura de Servicios para Gestión Clínica (UAGRM)",
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
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
# [SPRINT 0 - T005] Diseño del modelo de usuario extendido para soporte Multi-tenant (RF-29).
AUTH_USER_MODEL = "core.Usuario"  # [SPRINT 0 - T005] Modelo personalizado con roles y clínica

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# ==============================================================================
# SECCIÓN: LOCALIZACIÓN (ESTÁNDARES BOLIVIA | SPRINT 0)
# ==============================================================================
LANGUAGE_CODE = "es-bo"  # [SPRINT 0 - T009] Estándares de codificación: Localización Bolivia
TIME_ZONE = "America/La_Paz"  # [SPRINT 0 - T009] Zona horaria correcta para producción
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# [RENDER] Archivos persistentes gestionados por WhiteNoise
if not DEBUG:
    STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
# ==============================================================================
# SECCIÓN: REDIRECCIONES DE FLUJO (SOLUCIÓN T007 | SPRINT 0)
# CORRECCIÓN CAUSA RAÍZ #5: Arquitectura Pure REST
# ==============================================================================
# Se eliminan las redirecciones a vistas HTML (Arquitectura Híbrida)
# El flujo de navegación ahora es responsabilidad exclusiva del Frontend (React/Flutter)
LOGIN_URL = None
LOGIN_REDIRECT_URL = None
LOGOUT_REDIRECT_URL = None

# ==============================================================================
# SECCIÓN: LOGGING Y AUDITORÍA [SPRINT 1 - T023] [RF-30]
# ==============================================================================
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "audit": {
            "format": "[{asctime}] {levelname} {name}: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "audit",
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": BASE_DIR / "logs" / "audit.log",
            "formatter": "audit",
        },
    },
    "loggers": {
        "audit": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
        "core": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# ==============================================================================
# SECCIÓN: CORREO ELECTRÓNICO [SPRINT 1 - T020] [CU-03]
# ==============================================================================
# [SPRINT 1 - T020] Módulo SMTP para recuperación de contraseñas.
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL", default="noreply@psicosystem.com"
)

# ==============================================================================
# SECCIÓN: SEGURIDAD AVANZADA [SPRINT 1 - T026] [RNF-03]
# ==============================================================================
if not DEBUG:
    SECURE_BROWSER_XSS_FILTER = True  # [T026] Protección XSS
    SECURE_CONTENT_TYPE_NOSNIFF = True  # [T026] Prevenir MIME sniffing
    X_FRAME_OPTIONS = "DENY"  # [T026] Prevenir clickjacking
    SECURE_SSL_REDIRECT = True  # [T026] Forzar HTTPS
    SESSION_COOKIE_SECURE = True  # [T026] Cookies solo via HTTPS
    CSRF_COOKIE_SECURE = True  # [T026] CSRF cookie segura
    SECURE_HSTS_SECONDS = 31536000  # [T026] HSTS por 1 año
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
