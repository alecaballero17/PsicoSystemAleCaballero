from rest_framework import serializers
from .models import Clinica, Usuario, Paciente, Cita

# ==============================================================================
# SERIALIZERS: CAPA DE TRANSFORMACIÓN DE DATOS (JSON)
# TRAZABILIDAD: T008 (Arquitectura REST) | T011 (JWT) | SPRINT 1
# ==============================================================================


class ClinicaSerializer(serializers.ModelSerializer):
    """
    Trazabilidad: CU-25 (Registrar Clínica)
    Convierte el modelo Clinica a JSON para la API de administración.
    """

    class Meta:
        model = Clinica
        fields = ["id", "nombre", "nit", "direccion", "plan_suscripcion"]


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Trazabilidad: CU-01 | RF-01 (JWT)
    Maneja la representación de usuarios para la autenticación y perfiles.
    """

    class Meta:
        model = Usuario
        fields = ["id", "username", "email", "clinica", "rol"]


class PacienteSerializer(serializers.ModelSerializer):
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
    """
    Trazabilidad: T005 (Diseño BD)
    RF-28: Control de visibilidad de datos de agenda.
    """

    # RNF-08: Declarar campos explícitos es más seguro que "__all__"
    class Meta:
        model = Cita
        fields = ["id", "paciente", "psicologo", "fecha_hora", "estado"]
