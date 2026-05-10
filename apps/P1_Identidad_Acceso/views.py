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
from .models import Clinica, Usuario, TransaccionClinica
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
    TransaccionClinicaSerializer,
)
from .permissions import HasClinicaAsignada, EsPsicologoOAdministrador, EsAdministrador

logger = logging.getLogger(__name__)


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


class UsuarioPerfilAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT: Devuelve y actualiza los datos del usuario autenticado."""
    serializer_class = UsuarioSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class ChangePasswordAPIView(APIView):
    """PUT: Cambiar la contraseña del usuario autenticado."""
    permission_classes = [IsAuthenticated]
    
    def put(self, request):
        user = request.user
        new_password = request.data.get("new_password")
        if not new_password or len(new_password) < 8:
            return Response({"detail": "La contraseña debe tener al menos 8 caracteres."}, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        return Response({"detail": "Contraseña actualizada exitosamente."}, status=status.HTTP_200_OK)


class PlanesListAPIView(APIView):
    """GET público: devuelve el catálogo de planes configurados en el modelo Clínica, incluyendo PRECIOS para Stripe."""
    permission_classes = [AllowAny]

    def get(self, request):
        # Catálogo de precios y características de los planes SaaS
        catalogo = [
            {"id": "Basico", "nombre": "Plan Básico (Gratis)", "precio": 0.00, "duracion_dias": 365, "beneficios": "Gestión de 1 agenda, soporte por email."},
            {"id": "Profesional", "nombre": "Plan Profesional", "precio": 49.99, "duracion_dias": 30, "beneficios": "Hasta 5 agendas, recordatorios WhatsApp, IA Clínica."},
            {"id": "Premium", "nombre": "Plan Premium (Anual)", "precio": 499.99, "duracion_dias": 365, "beneficios": "Ilimitado, IA avanzada, analítica predictiva, soporte 24/7."}
        ]
        return Response(catalogo, status=status.HTTP_200_OK)


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


class MiClinicaRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):
    """GET/PUT/PATCH: Ver y actualizar datos de la clínica del usuario logueado."""
    serializer_class = ClinicaSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador]

    def get_object(self):
        return self.request.user.clinica

    def perform_update(self, serializer):
        if self.request.user.rol != 'ADMIN':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo el administrador puede modificar los datos de la clínica.")
        serializer.save()


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


class ClinicaPublicListAPIView(APIView):
    """GET público: devuelve lista básica de clínicas para el onboarding móvil."""
    permission_classes = [AllowAny]

    def get(self, request):
        clinicas = Clinica.objects.all().values("id", "nombre", "direccion", "plan_suscripcion")
        resultado = []
        for c in clinicas:
            # Simular especialidades base si es Premium
            especialidades = "Psicología General"
            if c["plan_suscripcion"] == "Premium":
                especialidades = "Psicología General, Psiquiatría, Terapia Familiar"
            elif c["plan_suscripcion"] == "Profesional":
                especialidades = "Psicología General, Terapia de Pareja"
                
            # Contar psicólogos
            psicologos_count = Usuario.objects.filter(clinica_id=c["id"], rol="PSICOLOGO").count()
            
            # Beneficios por plan para mostrar en móvil
            plan_beneficios = "Gestión básica de citas y pacientes."
            horario = "Lunes a Viernes, 09:00 - 18:00"
            if c["plan_suscripcion"] == "Profesional":
                plan_beneficios = "Soporte Prioritario, múltiples agendas, Análisis Básico."
                horario = "Lunes a Sábado, 08:00 - 20:00"
            elif c["plan_suscripcion"] == "Premium":
                plan_beneficios = "Análisis IA Avanzado, Reportes Predictivos, Soporte VIP."
                horario = "Atención 24/7 (Citas de Emergencia Disponibles)"
            
            resultado.append({
                "id": c["id"],
                "nombre": c["nombre"],
                "direccion": c["direccion"] if c["direccion"] else "Dirección no registrada",
                "especialidades": especialidades,
                "plan_suscripcion": c["plan_suscripcion"],
                "psicologos_count": psicologos_count,
                "plan_beneficios": plan_beneficios,
                "horario": horario
            })
            
        return Response(resultado, status=status.HTTP_200_OK)


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
        clinica = self.request.user.clinica
        # SaaS Feature-Gating: No hay límites de psicólogos en ningún plan.
        serializer.save(clinica=clinica, rol="PSICOLOGO")


class SuscripcionInfoAPIView(APIView):
    """GET: Devuelve el estado de la suscripción y uso de cupos de la clínica."""
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get(self, request, pk):
        clinica = request.user.clinica
        if str(clinica.id) != str(pk):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tienes acceso a esta suscripción.")
            
        from apps.P2_Gestion_Clinica.models import Paciente
        pacientes_count = Paciente.objects.filter(clinica=clinica).count()
        psicologos_count = Usuario.objects.filter(clinica=clinica, rol="PSICOLOGO").count()
        
        plan = clinica.plan_suscripcion
        info = {
            "clinica_id": clinica.id,
            "clinica_nombre": clinica.nombre,
            "saldo": float(clinica.saldo),
            "plan_nombre": f"Plan {plan}",
            "estado": "ACTIVA",
            "fecha_creacion": clinica.fecha_creacion.isoformat(),
            "uso": {
                "pacientes_actuales": pacientes_count,
                "pacientes_limite": "Ilimitado",
                "psicologos_actuales": psicologos_count,
                "psicologos_limite": "Ilimitado"
            },
            "features": {
                "soporte": "Estándar" if plan == "Basico" else "Prioritario 24h" if plan == "Profesional" else "VIP Dedicado 24/7",
                "ia_medica": False if plan == "Basico" else True,
                "auditoria_avanzada": False if plan == "Basico" else True,
            }
        }
        
        return Response(info, status=status.HTTP_200_OK)


class TransaccionClinicaListAPIView(generics.ListAPIView):
    """GET: Historial de transacciones de facturación de la clínica."""
    serializer_class = TransaccionClinicaSerializer
    permission_classes = [IsAuthenticated, EsAdministrador, HasClinicaAsignada]

    def get_queryset(self):
        return TransaccionClinica.objects.filter(clinica=self.request.user.clinica).order_by("-fecha")


class CargarSaldoAPIView(APIView):
    """POST: Cargar saldo a la cuenta de la clínica."""
    permission_classes = [IsAuthenticated, EsAdministrador, HasClinicaAsignada]

    def post(self, request):
        clinica = request.user.clinica
        monto = request.data.get("monto")
        descripcion = request.data.get("descripcion", "Carga de saldo manual")
        
        if not monto or float(monto) <= 0:
            return Response({"detail": "Monto inválido."}, status=status.HTTP_400_BAD_REQUEST)
        
        import decimal
        clinica.saldo += decimal.Decimal(monto)
        clinica.save()
        
        TransaccionClinica.objects.create(
            clinica=clinica,
            tipo='CARGA',
            monto=monto,
            descripcion=descripcion,
            metodo_pago=request.data.get("metodo_pago", "TRANSFERENCIA")
        )
        
        return Response({"detail": "Saldo cargado exitosamente.", "nuevo_saldo": float(clinica.saldo)}, status=status.HTTP_200_OK)


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
