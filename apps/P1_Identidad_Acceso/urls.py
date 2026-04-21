from django.urls import path
from django.contrib.auth import views as auth_views
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView

from .views import (
    registrar_usuario_view,
    CustomTokenObtainPairView,
    RegistroPsicologoAPIView,
    MiClinicaRetrieveAPIView,
    ClinicaCreateAPIView,
    UsuarioColaboradorListCreateAPIView,
    UsuarioAdminRetrieveUpdateDestroyAPIView,
    PsicologoListCreateAPIView,
    PsicologoRetrieveUpdateDestroyAPIView,
    PlanesListAPIView,
    OnboardingSaaSAPIView,
)

urlpatterns = [
    # Password reset (API-compatible, redirige por email)
    path("password_reset/", auth_views.PasswordResetView.as_view(), name="password_reset"),
    path("password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    # JWT endpoints — login usa la vista custom con throttle + bloqueo
    path("api/auth/login/", CustomTokenObtainPairView.as_view(), name="api_login"),
    path("api/auth/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/logout/", TokenBlacklistView.as_view(), name="api_logout_blacklist"),
    path(
        "api/auth/registro/psicologo/",
        RegistroPsicologoAPIView.as_view(),
        name="api_registro_psicologo",
    ),
    path("api/planes/", PlanesListAPIView.as_view(), name="api_planes_list"),
    path("api/onboarding/", OnboardingSaaSAPIView.as_view(), name="api_onboarding_saas"),
    path("api/clinicas/mi/", MiClinicaRetrieveAPIView.as_view(), name="api_mi_clinica"),
    path("api/clinicas/", ClinicaCreateAPIView.as_view(), name="api_registrar_clinica"),
    path(
        "api/usuarios/",
        UsuarioColaboradorListCreateAPIView.as_view(),
        name="api_usuarios",
    ),
    path(
        "api/usuarios/<int:pk>/",
        UsuarioAdminRetrieveUpdateDestroyAPIView.as_view(),
        name="api_usuario_detail",
    ),
    # ── Psicólogos (T017) ──
    path(
        "api/psicologos/",
        PsicologoListCreateAPIView.as_view(),
        name="api_psicologos",
    ),
    path(
        "api/psicologos/<int:pk>/",
        PsicologoRetrieveUpdateDestroyAPIView.as_view(),
        name="api_psicologo_detail",
    ),
]
