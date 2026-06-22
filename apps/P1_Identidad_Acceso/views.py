import logging

from django.shortcuts import render, redirect, get_object_or_404
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
    """GET: Devuelve los datos del usuario autenticado. Usado por el frontend para verificar sesión.
    PUT: Actualiza los campos de preferencias del usuario.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.pk,
            "username": user.username,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "ci": user.last_name, # Para la App Móvil
            "rol": user.rol,
            "clinica_id": user.clinica_id,
            "clinica_nombre": user.clinica.nombre if user.clinica else None,
            "email_notif_citas": user.email_notif_citas,
            "email_notif_reportes": user.email_notif_reportes,
            "push_notif_alertas": user.push_notif_alertas,
        }, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        if "email_notif_citas" in request.data:
            user.email_notif_citas = request.data["email_notif_citas"]
        if "email_notif_reportes" in request.data:
            user.email_notif_reportes = request.data["email_notif_reportes"]
        if "push_notif_alertas" in request.data:
            user.push_notif_alertas = request.data["push_notif_alertas"]
        user.save()
        return Response({
            "status": "success",
            "email_notif_citas": user.email_notif_citas,
            "email_notif_reportes": user.email_notif_reportes,
            "push_notif_alertas": user.push_notif_alertas,
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
        # [SaaS Limits Check]
        clinica = self.request.user.clinica
        plan = clinica.plan_suscripcion if clinica else 'Basico'
        limite = 2 if plan == 'Basico' else (10 if plan == 'Profesional' else 9999)
        actual = Usuario.objects.filter(clinica=clinica, rol='PSICOLOGO').count()
        if actual >= limite:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Límite excedido: Tu plan actual ({plan}) solo permite registrar hasta {limite} psicólogos.")

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

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated()]
        return [IsAuthenticated(), EsPsicologoOAdministrador(), HasClinicaAsignada()]

    def get_queryset(self):
        queryset = Usuario.objects.filter(rol="PSICOLOGO")
        
        if self.request.user.rol == 'PACIENTE':
            clinica_id = self.request.query_params.get('clinica_id', None)
            # Permite a los móviles filtrar los psicólogos por una clínica específica
            if clinica_id:
                queryset = queryset.filter(clinica_id=clinica_id)
        else:
            # Para el panel web, los admins/psicólogos solo ven a los de su propia clínica
            queryset = queryset.filter(clinica=self.request.user.clinica)
            
        return queryset.order_by("first_name", "last_name")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return PsicologoCreateSerializer
        return PsicologoSerializer

    def perform_create(self, serializer):
        # [SaaS Limits Check]
        clinica = self.request.user.clinica
        plan = clinica.plan_suscripcion if clinica else 'Basico'
        limite = 2 if plan == 'Basico' else (10 if plan == 'Profesional' else 9999)
        actual = Usuario.objects.filter(clinica=clinica, rol='PSICOLOGO').count()
        if actual >= limite:
            from rest_framework.exceptions import ValidationError
            raise ValidationError(f"Límite excedido: Tu plan actual ({plan}) solo permite registrar hasta {limite} psicólogos.")

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


class SuscripcionClinicaAPIView(APIView):
    """
    Endpoint para ver y actualizar el estado de la suscripción SaaS y los límites de la clínica (CU-24).
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get(self, request, clinica_id):
        # Validar pertenencia al Tenant para aislamiento estricto (RF-29)
        if not request.user.is_superuser and request.user.clinica_id != int(clinica_id):
            return Response({"error": "No tienes acceso a la suscripción de esta clínica."}, status=status.HTTP_403_FORBIDDEN)

        clinica = get_object_or_404(Clinica, pk=clinica_id)
        plan = clinica.plan_suscripcion or 'Basico'

        # Límites por plan
        if plan == 'Basico':
            pacientes_limite = 5
            psicologos_limite = 2
            plan_nombre = "Plan Básico (Gratuito)"
        elif plan == 'Profesional':
            pacientes_limite = 20
            psicologos_limite = 10
            plan_nombre = "Plan Profesional"
        else: # Premium
            pacientes_limite = 9999
            psicologos_limite = 9999
            plan_nombre = "Plan Premium (SaaS Full)"

        # Contar registros actuales de la clínica
        from apps.P2_Gestion_Clinica.models import Paciente
        pacientes_actuales = Paciente.objects.filter(clinica=clinica).count()
        psicologos_actuales = Usuario.objects.filter(clinica=clinica, rol='PSICOLOGO').count()

        return Response({
            "clinica_nombre": clinica.nombre,
            "plan_nombre": plan_nombre,
            "estado": "ACTIVA",
            "fecha_inicio": "2026-05-01T00:00:00Z",
            "uso": {
                "pacientes_actuales": pacientes_actuales,
                "pacientes_limite": pacientes_limite,
                "psicologos_actuales": psicologos_actuales,
                "psicologos_limite": psicologos_limite,
            }
        }, status=status.HTTP_200_OK)

    def put(self, request, clinica_id):
        # Actualización de plan con simulación de Stripe Checkout
        if not request.user.is_superuser and request.user.clinica_id != int(clinica_id):
            return Response({"error": "No tienes acceso para modificar la suscripción de esta clínica."}, status=status.HTTP_403_FORBIDDEN)

        clinica = get_object_or_404(Clinica, pk=clinica_id)
        nuevo_plan = request.data.get("plan_suscripcion")

        if nuevo_plan not in ['Basico', 'Profesional', 'Premium']:
            return Response({"error": "El plan de suscripción seleccionado no es válido."}, status=status.HTTP_400_BAD_REQUEST)

        clinica.plan_suscripcion = nuevo_plan
        clinica.save()

        # Registrar la acción en la bitácora de auditoría (RF-30)
        from apps.P4_IA_Administracion.models import LogAuditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Actualizó la suscripción de la clínica al plan: {nuevo_plan} (Transacción Stripe completada)."
        )

        return Response({
            "message": f"Suscripción actualizada exitosamente al plan {nuevo_plan}.",
            "plan_suscripcion": nuevo_plan
        }, status=status.HTTP_200_OK)


from rest_framework.permissions import AllowAny

class ClinicaPublicListAPIView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        clinicas = Clinica.objects.all().values("id", "nombre", "direccion", "plan_suscripcion")
        resultado = []
        for c in clinicas:
            especialidades = "Psicología General"
            if c["plan_suscripcion"] == "Premium":
                especialidades = "Psicología General, Psiquiatría, Terapia Familiar"
            elif c["plan_suscripcion"] == "Profesional":
                especialidades = "Psicología General, Terapia de Pareja"
                
            psicologos_count = Usuario.objects.filter(clinica_id=c["id"], rol="PSICOLOGO").count()
            
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
