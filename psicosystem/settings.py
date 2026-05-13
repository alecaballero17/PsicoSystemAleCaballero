"""
Configuración principal de PsicoSystem SI2.
"""
from pathlib import Path
from datetime import timedelta
import os
import dj_database_url
from decouple import config  # RNF-03: Seguridad de credenciales | SPRINT 0
from django.core.exceptions import ImproperlyConfigured

# Parche para evitar error de "drf_format_suffix already registered" en Django 5/6+
from django.urls import converters
_original_register_converter = converters.register_converter
def _patched_register_converter(converter, type_name):
    try:
        _original_register_converter(converter, type_name)
    except ValueError as e:
        if "already registered" in str(e):
            pass
        else:
            raise
converters.register_converter = _patched_register_converter

BASE_DIR = Path(__file__).resolve().parent.parent

# ==============================================================================
# SECCIÓN: SEGURIDAD (RNF-03 | PUNTO 12 AUDITORÍA | SPRINT 0)
# ==============================================================================
# T001: Definición de arquitectura segura.
# Se utiliza 'decouple' para evitar el hardcodeo de llaves, cumpliendo con RNF-03.
SECRET_KEY = config("SECRET_KEY", default=None)

# T004: Configuración del entorno de desarrollo.
DEBUG = config("DEBUG", default=True, cast=bool)

if not SECRET_KEY:
    if DEBUG:
        SECRET_KEY = "django-insecure-psicosystem-2026-audit-fix"
    else:
        raise ImproperlyConfigured(
            "La variable de entorno SECRET_KEY es obligatoria en producción."
        )

# Hosts permitidos: Detección automática para Railway y Render
ALLOWED_HOSTS = [
    h.strip()
    for h in config(
        "ALLOWED_HOSTS",
        default="localhost,127.0.0.1",
    ).split(",")
    if h.strip()
]

# Detección de Railway
_railway_static_url = os.environ.get("RAILWAY_STATIC_URL")
if _railway_static_url:
    ALLOWED_HOSTS.append(_railway_static_url)
    ALLOWED_HOSTS.append(".railway.app")

# Detección de Render
_render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")
if _render_host:
    ALLOWED_HOSTS.append(_render_host)
    ALLOWED_HOSTS.append(".onrender.com")

# Detrás del proxy HTTPS de Render, sin esto las cookies/CSRF suelen fallar (login “no avanza”)
if os.environ.get("RENDER"):
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=not DEBUG, cast=bool)
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# HSTS en entornos seguros
if not DEBUG:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True

# Orígenes explícitos para el token CSRF en HTTPS (Django 4+)
_csrf_origins = config("CSRF_TRUSTED_ORIGINS", default="").strip()
if _csrf_origins:
    CSRF_TRUSTED_ORIGINS = [o.strip() for o in _csrf_origins.split(",") if o.strip()]
else:
    CSRF_TRUSTED_ORIGINS = []
    if _render_host:
        CSRF_TRUSTED_ORIGINS.append(f"https://{_render_host}")
    if _railway_static_url:
        CSRF_TRUSTED_ORIGINS.append(f"https://{_railway_static_url}")

# ==============================================================================
# SECCIÓN: DEFINICIÓN DE APLICACIONES (T001, T002 | SPRINT 0)
# ==============================================================================
INSTALLED_APPS = [
    "apps.P1_Identidad_Acceso",
    "apps.P2_Gestion_Clinica",
    "apps.P3_Logistica_Citas",
    "apps.P4_IA_Administracion",
    "rest_framework",  # T008: Conexión básica para arquitectura REST (API).
    "rest_framework_simplejwt",  # RF-01: Autenticación JWT (Sprint 1 - T011).
    "rest_framework_simplejwt.token_blacklist", # T022: Invalidación de Token JWT
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",  # <--- AGREGAR ESTA LÍNEA
    "django_extensions",
    "drf_spectacular",
]

MIDDLEWARE = [
    # "corsheaders.middleware.CorsMiddleware",  # TEMP DISABLED: isolating middleware failure
    "django.middleware.security.SecurityMiddleware",
    # "whitenoise.middleware.WhiteNoiseMiddleware",  # TEMP DISABLED: may fail on missing staticfiles
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",  # RNF-03: Seguridad contra ataques CSRF.
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Sin LoginRequiredMiddleware: el registro y el login deben ser públicos; el acceso se controla con
    # @login_required en dashboard, pacientes, etc. (el middleware global rompía /registro-psicologo/ en Render).
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
    "default": dj_database_url.config(
        default=config(
            "DATABASE_URL",
            default="sqlite:///" + str(BASE_DIR / "db.sqlite3"),
        ),
        conn_max_age=600,
    )
}

# En desarrollo local, se permite un DB_PASSWORD por defecto; en producción siempre defínelo.
if not os.environ.get("DATABASE_URL"):
    DATABASES["default"]["PASSWORD"] = config("DB_PASSWORD", default="1234")

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
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",
        "user": "60/minute",
        "login": "5/minute",
        "registro": "3/minute",
    },
}

# Configuración de Documentación Profesional (drf-spectacular)
SPECTACULAR_SETTINGS = {
    'TITLE': 'PsicoSystem SI2 API',
    'DESCRIPTION': 'Documentación técnica de la plataforma de gestión psicológica con IA.',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'COMPONENT_SPLIT_PATCH': True,
    'COMPONENT_SPLIT_CREATABLE': True,
}

# RF-01: Parámetros del ciclo de vida del Token (Seguridad Stateless).
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "TOKEN_OBTAIN_SERIALIZER": "apps.P1_Identidad_Acceso.serializers.CustomTokenObtainPairSerializer",
}

# ==============================================================================
# SECCIÓN: GESTIÓN DE IDENTIDAD (RF-28 | ROLES | SPRINT 0)
# ==============================================================================
# T005: Diseño del modelo de usuario extendido para soporte Multi-tenant (RF-29).
AUTH_USER_MODEL = "P1_Identidad_Acceso.Usuario"

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
STATIC_ROOT = BASE_DIR / "staticfiles" # Requerido por WhiteNoise en Producción

# ==============================================================================
# SECCIÓN: REDIRECCIONES DE FLUJO (SOLUCIÓN T007 | SPRINT 0)
# ==============================================================================
# CU-01: Inicio de sesión.
LOGIN_URL = "/login/"
# T007: Cumplimiento del Prototipo UI (Dashboard funcional).
LOGIN_REDIRECT_URL = "/dashboard/"
LOGOUT_REDIRECT_URL = "/login/"

# Configuración de CORS para Interoperabilidad (RNF)
# En producción se recomienda definir explícitamente los orígenes permitidos.
CORS_ALLOW_ALL_ORIGINS = config("CORS_ALLOW_ALL_ORIGINS", default=DEBUG, cast=bool)
_cors_origins = config("CORS_ALLOWED_ORIGINS", default="").strip()
if _cors_origins:
    CORS_ALLOWED_ORIGINS = [o.strip() for o in _cors_origins.split(",") if o.strip()]
elif _render_host:
    CORS_ALLOWED_ORIGINS = [f"https://{_render_host}"]

CORS_ALLOW_CREDENTIALS = True

# ============================================================================== 
# SECCIÓN: COMUNICACIONES (T019, T020 | Recuperación de Contraseña)
# ==============================================================================
# Por defecto consola; en Render define EMAIL_BACKEND=smtp y las variables SMTP.
EMAIL_BACKEND = config(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
EMAIL_HOST = config("EMAIL_HOST", default="")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="soporte@psicosystem.com")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config(
    "DEFAULT_FROM_EMAIL",
    default=EMAIL_HOST_USER or "noreply@psicosystem.local",
)
