from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .models import Clinica, Usuario


# --------------------------------------------------------------------------
# JWT: Claims custom (rol, clinica_id) en el token
# --------------------------------------------------------------------------
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token["rol"] = user.rol
        token["clinica_id"] = user.clinica_id
        token["username"] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        # RF-29 / Frontend: Enviar estas propiedades en la raíz de la respuesta JSON
        # para que authService.js (React) y AuthService (Flutter) puedan leerlos directamente
        data["role"] = self.user.rol
        data["clinica_id"] = self.user.clinica_id
        data["username"] = self.user.username

        # Disparar señal de Django para la bitácora P4 (React/Flutter login)
        from django.contrib.auth.signals import user_logged_in
        user_logged_in.send(sender=self.user.__class__, request=self.context.get('request'), user=self.user)

        return data


class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = ["id", "nombre", "nit", "direccion", "plan_suscripcion"]


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "id", "username", "email", "first_name", "last_name", 
            "clinica", "rol", "especialidad", "telefono"
        ]


class UsuarioColegaCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            "username",
            "email",
            "first_name",
            "last_name",
            "especialidad",
            "telefono",
            "password",
            "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegistroPsicologoAPISerializer(serializers.Serializer):
    """Registro público de clínica + primer psicólogo (para app móvil / API)."""

    nombre_clinica = serializers.CharField(max_length=100)
    nit_clinica = serializers.CharField(max_length=20)
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField()
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    def validate_nit_clinica(self, value):
        if Clinica.objects.filter(nit=value).exists():
            raise serializers.ValidationError("Ya existe una clínica con este NIT.")
        return value

    def validate_username(self, value):
        if Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        nombre_clinica = validated_data.pop("nombre_clinica")
        nit_clinica = validated_data.pop("nit_clinica")

        clinica = Clinica.objects.create(
            nombre=nombre_clinica,
            nit=nit_clinica,
            direccion="",
            plan_suscripcion="Basico",
        )
        user = Usuario(
            username=validated_data["username"],
            email=validated_data.get("email", ""),
            first_name=validated_data.get("first_name", ""),
            last_name=validated_data.get("last_name", ""),
            clinica=clinica,
            rol="PSICOLOGO",
        )
        user.set_password(password)
        user.save()
        return user


# --------------------------------------------------------------------------
# ONBOARDING SAAS: Registro unificado de Clínica + Admin (React atomic flow)
# --------------------------------------------------------------------------
class ClinicaOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = ["nombre", "nit", "direccion"]

class AdminOnboardingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["username", "email", "password"]
        extra_kwargs = {'password': {'write_only': True}}

class OnboardingSaaSSerializer(serializers.Serializer):
    clinica = ClinicaOnboardingSerializer()
    admin = AdminOnboardingSerializer()
    plan_id = serializers.ChoiceField(choices=Clinica.PLANES)

    def validate_clinica(self, value):
        if Clinica.objects.filter(nit=value.get('nit')).exists():
            raise serializers.ValidationError("Ya existe una clínica con este NIT.")
        return value

    def validate_admin(self, value):
        if Usuario.objects.filter(username=value.get('username')).exists():
            raise serializers.ValidationError("Este nombre de usuario ya está en uso.")
        return value

    def create(self, validated_data):
        clinica_data = validated_data.pop('clinica')
        admin_data = validated_data.pop('admin')
        plan_id = validated_data.pop('plan_id')

        # 1. Crear Clínica con el plan seleccionado
        clinica = Clinica.objects.create(
            **clinica_data,
            plan_suscripcion=plan_id
        )

        # 2. Crear SuperAdmin del Tenant
        password = admin_data.pop('password')
        user = Usuario(
            **admin_data,
            clinica=clinica,
            rol="ADMIN"
        )
        user.set_password(password)
        user.save()

        return {"clinica": clinica, "admin": user}


# --------------------------------------------------------------------------
# Admin: serializer para actualizar rol / estado de usuarios
# --------------------------------------------------------------------------
class UsuarioAdminUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "first_name", "last_name", "email", "rol", "is_active", 
            "especialidad", "telefono"
        ]

    def validate_rol(self, value):
        roles_validos = {r[0] for r in Usuario.ROLES}
        if value not in roles_validos:
            raise serializers.ValidationError("Rol no válido.")
        return value


# --------------------------------------------------------------------------
# Psicólogos: serializers para CRUD de profesionales
# --------------------------------------------------------------------------
class PsicologoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "id", "username", "email", "first_name", "last_name",
            "especialidad", "telefono", "is_active",
        ]


class PsicologoCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = Usuario
        fields = [
            "username", "email", "first_name", "last_name",
            "especialidad", "telefono", "password", "password_confirm",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password_confirm": "Las contraseñas no coinciden."}
            )
        validate_password(attrs["password"])
        return attrs

    def create(self, validated_data):
        validated_data.pop("password_confirm")
        password = validated_data.pop("password")
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class PsicologoUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = [
            "first_name", "last_name", "email",
            "especialidad", "telefono",
        ]
