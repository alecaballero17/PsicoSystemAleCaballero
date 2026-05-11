import logging

from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.core.cache import cache
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import generics, status
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from .forms import RegistroPsicologoCompletoForm
from .models import Clinica, Usuario
from .serializers import (
    ClinicaSerializer,
    UsuarioSerializer,
    UsuarioColegaCreateSerializer,
    UsuarioAdminUpdateSerializer,
    RegistroPsicologoAPISerializer,
    PsicologoSerializer,
    PsicologoCreateSerializer,
    PsicologoUpdateSerializer,
    OnboardingSaaSSerializer,
)
from .permissions import HasClinicaAsignada, EsPsicologoOAdministrador, EsAdministrador

logger = logging.getLogger(__name__)


# ==========================================================================
# Endpoint /api/auth/me/ — Verificación de sesión JWT (Anti-huérfano)
# ==========================================================================
class MeAPIView(APIView):
    """GET: Devuelve los datos del usuario autenticado. Usado por el frontend para verificar sesión."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "rol": user.rol,
            "clinica_id": user.clinica_id,
            "clinica_nombre": user.clinica.nombre if user.clinica else None,
        }, status=status.HTTP_200_OK)



# ==========================================================================
# Login API con rate-limit y bloqueo por intentos fallidos (cache-based)
# ==========================================================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_SECONDS = 900  # 15 minutos


class CustomTokenObtainPairView(TokenObtainPairView):
    """Login JWT con throttle y bloqueo temporal por intentos fallidos."""

    throttle_scope = "login"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request, *args, **kwargs):
        username = request.data.get("username", "")
        cache_key = f"login_attempts_{username}"
        attempts = cache.get(cache_key, 0)

        if attempts >= MAX_LOGIN_ATTEMPTS:
            return Response(
                {
                    "detail": "Cuenta bloqueada temporalmente por múltiples intentos fallidos. "
                    "Intenta en 15 minutos."
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        try:
            response = super().post(request, *args, **kwargs)
        except Exception:
            cache.set(cache_key, attempts + 1, LOCKOUT_SECONDS)
            raise

        # Login exitoso → resetear contador
        cache.delete(cache_key)
        return response


# ==========================================================================
# Registro de psicólogo — vista de plantilla (formulario HTML)
# ==========================================================================
REGISTRO_MAX_POR_IP = 3
REGISTRO_VENTANA = 3600  # 1 hora


def registrar_usuario_view(request):
    if request.method == "POST":
        # Rate-limit simple por IP para evitar spam de registros
        ip = request.META.get("HTTP_X_FORWARDED_FOR", request.META.get("REMOTE_ADDR", "")).split(",")[0].strip()
        cache_key = f"registro_rate_{ip}"
        intentos = cache.get(cache_key, 0)
        if intentos >= REGISTRO_MAX_POR_IP:
            logger.warning("Registro bloqueado por rate-limit: IP=%s", ip)
            return render(
                request,
                "P1_Identidad_Acceso/registrar_usuario.html",
                {"form": RegistroPsicologoCompletoForm(), "rate_limited": True},
            )

        form = RegistroPsicologoCompletoForm(request.POST)
        if form.is_valid():
            nueva_clinica = Clinica.objects.create(
                nombre=form.cleaned_data["nombre_clinica"],
                nit=form.cleaned_data["nit_clinica"],
                direccion="",
                plan_suscripcion="Basico",
            )

            usuario = form.save(commit=False)
            usuario.clinica = nueva_clinica
            usuario.rol = "PSICOLOGO"
            usuario.save()

            cache.set(cache_key, intentos + 1, REGISTRO_VENTANA)
            login(request, usuario)
            return redirect("dashboard")
        logger.warning("Registro inválido: %s", form.errors)
    else:
        form = RegistroPsicologoCompletoForm()
    return render(request, "P1_Identidad_Acceso/registrar_usuario.html", {"form": form})


class RegistroPsicologoAPIView(APIView):
    """POST público: alta clínica + usuario psicólogo; devuelve tokens JWT (móvil / Postman)."""

    permission_classes = [AllowAny]
    throttle_scope = "registro"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = RegistroPsicologoAPISerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response(
            {
                "message": "Cuenta creada correctamente.",
                "user": UsuarioSerializer(user).data,
                "tokens": {
                    "refresh": str(refresh),
                    "access": str(refresh.access_token),
                },
            },
            status=status.HTTP_201_CREATED,
        )


class PlanesListAPIView(APIView):
    """GET público: devuelve el catálogo de planes configurados en el modelo Clínica."""
    permission_classes = [AllowAny]

    def get(self, request):
        planes = [
            {"id": p[0], "nombre": p[1]} 
            for p in Clinica.PLANES
        ]
        return Response(planes, status=status.HTTP_200_OK)


class OnboardingSaaSAPIView(APIView):
    """POST público: alta atómica de Clínica + Administrador con selección de Plan."""
    permission_classes = [AllowAny]
    throttle_scope = "registro"
    throttle_classes = [ScopedRateThrottle]

    def post(self, request):
        serializer = OnboardingSaaSSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        result = serializer.save()
        return Response(
            {
                "message": "Entorno SaaS configurado correctamente.",
                "clinica_id": result["clinica"].id,
                "admin_username": result["admin"].username
            },
            status=status.HTTP_201_CREATED
        )


class MiClinicaRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = ClinicaSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get_object(self):
        return self.request.user.clinica


class ClinicaCreateAPIView(APIView):
    """Alta de clínica adicional: solo rol ADMIN con clínica asignada."""

    permission_classes = [IsAuthenticated, EsAdministrador, HasClinicaAsignada]

    def post(self, request):
        serializer = ClinicaSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Clínica registrada"}, status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UsuarioColaboradorListCreateAPIView(generics.ListCreateAPIView):
    """Lista psicólogos/usuarios de la misma clínica; POST crea colega (rol PSICOLOGO)."""

    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return Usuario.objects.filter(clinica=self.request.user.clinica).order_by(
            "username"
        )

    def get_serializer_class(self):
        if self.request.method == "POST":
            return UsuarioColegaCreateSerializer
        return UsuarioSerializer

    def perform_create(self, serializer):
        serializer.save(clinica=self.request.user.clinica, rol="PSICOLOGO")


# ==========================================================================
# CRUD completo de usuarios para ADMIN (ver, editar rol, desactivar)
# ==========================================================================
class UsuarioAdminRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE de un usuario de la misma clínica (solo ADMIN)."""

    permission_classes = [IsAuthenticated, EsAdministrador, HasClinicaAsignada]
    lookup_field = "pk"

    def get_queryset(self):
        return Usuario.objects.filter(clinica=self.request.user.clinica)

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return UsuarioAdminUpdateSerializer
        return UsuarioSerializer

    def perform_destroy(self, instance):
        """Soft-delete: desactivar en lugar de eliminar."""
        if instance.pk == self.request.user.pk:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("No puedes desactivarte a ti mismo.")
        instance.is_active = False
        instance.save()


# ==========================================================================
# CRUD de psicólogos (T017) — endpoints para web y móvil
# ==========================================================================
class PsicologoListCreateAPIView(generics.ListCreateAPIView):
    """GET: psicólogos de la clínica. POST: alta de nuevo psicólogo."""

    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador, HasClinicaAsignada]

    def get_queryset(self):
        return Usuario.objects.filter(
            clinica=self.request.user.clinica,
            rol="PSICOLOGO",
        ).order_by("first_name", "last_name")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PsicologoCreateSerializer
        return PsicologoSerializer

    def perform_create(self, serializer):
        serializer.save(clinica=self.request.user.clinica, rol="PSICOLOGO")


class PsicologoRetrieveUpdateDestroyAPIView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PUT/PATCH/DELETE de un psicólogo de la misma clínica."""

    permission_classes = [IsAuthenticated, EsPsicologoOAdministrador, HasClinicaAsignada]
    lookup_field = "pk"

    def get_queryset(self):
        return Usuario.objects.filter(
            clinica=self.request.user.clinica,
            rol="PSICOLOGO",
        )

    def get_serializer_class(self):
        if self.request.method in ("PUT", "PATCH"):
            return PsicologoUpdateSerializer
        return PsicologoSerializer

    def perform_destroy(self, instance):
        """Soft-delete: desactivar en lugar de eliminar."""
        if instance.pk == self.request.user.pk:
            from rest_framework.exceptions import ValidationError

            raise ValidationError("No puedes desactivarte a ti mismo.")
        instance.is_active = False
        instance.save()
