"""Serializers for PsicoSystem API.

This module defines ModelSerializers for core models and a custom JWT token serializer.
"""

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import Clinica, Usuario, Paciente, Cita

# ==============================================================================
# SERIALIZERS: CAPA DE TRANSFORMACIÓN DE DATOS (JSON)
# TRAZABILIDAD: T008 (Arquitectura REST) | T011 (JWT) | SPRINT 1
# ==============================================================================


class ClinicaSerializer(serializers.ModelSerializer):
    """Serializer for Clinica model.

    Maps Clinica fields to JSON representation for API consumption.
    """

    """
    Trazabilidad: CU-25 (Registrar Clínica)
    Convierte el modelo Clinica a JSON para la API de administración.
    """

    class Meta:
        model = Clinica
        fields = ["id", "nombre", "nit", "direccion", "plan_suscripcion"]


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Trazabilidad: CU-01 | RF-01 (JWT) | RF-28 (Roles)
    Maneja la representación de usuarios con validación de integridad organizacional.
    """

    class Meta:
        model = Usuario
        # Incluimos password para creación, pero lo protegemos con write_only
        fields = ["id", "username", "email", "password", "clinica", "rol"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_clinica(self, value):
        """
        RNF-08: Validación de datos de negocio.
        Garantiza que ningún usuario (Psicólogo/Admin) se cree sin una clínica raíz.
        """
        if not value:
            raise serializers.ValidationError(
                "Es obligatorio asignar una clínica para cumplir con el aislamiento de datos (RF-29)."
            )
        return value

    def create(self, validated_data):
        """
        Sobrescribimos para encriptar la contraseña correctamente al crear vía API.
        """
        user = Usuario.objects.create_user(**validated_data)
        return user


class PacienteSerializer(serializers.ModelSerializer):
    """Serializer for Paciente model, used by mobile app to submit patient data."""

    """
    Trazabilidad: T014 (Registro API) | RF-02 (Gestión Pacientes)
    Este es el motor de la T014. Permite que la App móvil envíe pacientes.
    """

    class Meta:
        model = Paciente
        fields = [
            "id",
            "nombre",
            "ci",
            "fecha_nacimiento",
            "telefono",
            "motivo_consulta",
        ]
        # Nota: 'clinica' no se incluye en fields para que el usuario no lo manipule,
        # se asigna automáticamente en la vista (RF-29).


class CitaSerializer(serializers.ModelSerializer):
    """Serializer for Cita model, representing appointments."""

    """
    Trazabilidad: T005 (Diseño BD)
    RF-28: Control de visibilidad de datos de agenda.
    """

    # RNF-08: Declarar campos explícitos es más seguro que "__all__"
    class Meta:
        model = Cita
        fields = ["id", "paciente", "psicologo", "fecha_hora", "estado"]


# ==============================================================================
# SEGURIDAD Y AUTHENTICACIÓN PERSONALIZADA (RF-01)
# ==============================================================================
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Trazabilidad: RF-01 (JWT), RF-28 (Roles), RF-29 (Multi-tenant)
    Inyecta metadatos del usuario en la respuesta del Login para optimizar el Frontend.
    """

    def validate(self, attrs):
        # Generamos los tokens estándar (access y refresh)
        data = super().validate(attrs)

        # Inyectamos datos adicionales para que React/Flutter no hagan peticiones extra
        data["role"] = self.user.rol
        data["username"] = self.user.username

        if self.user.clinica:
            data["clinica_id"] = self.user.clinica.id
            data["clinica_nombre"] = self.user.clinica.nombre
        else:
            data["clinica_id"] = None
            data["clinica_nombre"] = "Administrador Global"

        return data
