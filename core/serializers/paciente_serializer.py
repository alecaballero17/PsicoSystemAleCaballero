"""
[SPRINT 1 - T014] Endpoints de Registro: Serialización de datos de pacientes.
[RF-02] Registro de Pacientes: Motor de validación y persistencia del alta clínica.
[RF-29] Aislamiento SaaS: La 'clínica' se inyecta desde la vista (no expuesta al cliente).
[CU-02] Registro de Paciente (Onboarding): Valida los campos maestros del expediente.
"""
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from core.models import Paciente, Clinica, Usuario



class PacienteSerializer(serializers.ModelSerializer):
    """
    Serializer for Paciente model.
    Trazabilidad: T014 (Registro API) | RF-02 (Gestión Pacientes)
    Este es el motor de la T014. Permite que la App móvil envíe pacientes al Backend.
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
            "origen",
        ]

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')
        # [SEGURIDAD RNF-03] Aislamiento de Capas Clínicas
        if request and hasattr(request.user, 'rol') and request.user.rol == 'ADMIN':
            representation['motivo_consulta'] = '[ACCESO RESTRINGIDO - RNF-03]'
        return representation


class PacienteRegistroPublicoSerializer(serializers.Serializer):
    """
    [SPRINT 1 - T015] Flujo de Autogestión de credenciales por el Paciente.
    """
    clinica_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    nombre = serializers.CharField(max_length=100)
    ci = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate_clinica_id(self, value):
        # [SPRINT 1 - RF-29] Vinculación inicial de Tenant en el registro público (Ahora Opcional).
        if value is None:
            return None
        try:
            return Clinica.objects.get(pk=value)
        except Clinica.DoesNotExist:
            raise serializers.ValidationError("La clínica seleccionada no existe.")

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists() or Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_ci(self, value):
        if Paciente.objects.filter(ci=value).exists():
            raise serializers.ValidationError("Esta Cédula de Identidad ya está registrada.")
        return value

    def create(self, validated_data):
        clinica = validated_data.pop('clinica_id', None)
        nombre = validated_data['nombre']
        ci = validated_data['ci']
        email = validated_data['email']
        raw_password = validated_data['password']

        # Crear Usuario con rol PACIENTE
        usuario = Usuario.objects.create(
            username=email,
            email=email,
            password=make_password(raw_password),
            rol='PACIENTE',
            clinica=clinica
        )

        # Crear Paciente asociado
        paciente = Paciente.objects.create(
            nombre=nombre,
            ci=ci,
            email=email,
            clinica=clinica,
            fecha_nacimiento="1900-01-01",
            telefono="00000000",
            origen="MOVIL"
        )

        return {
            "nombre": paciente.nombre,
            "ci": paciente.ci,
            "email": usuario.email,
        }
