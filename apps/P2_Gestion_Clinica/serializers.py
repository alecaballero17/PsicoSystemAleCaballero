from rest_framework import serializers
from .models import Paciente, HistoriaClinica, EvolucionClinica
from apps.P1_Identidad_Acceso.models import Usuario, Clinica

class EvolucionClinicaSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.username')

    class Meta:
        model = EvolucionClinica
        fields = [
            "id", "historia", "psicologo", "psicologo_nombre", 
            "fecha_sesion", "notas_sesion", "archivo_adjunto", "analisis_ia"
        ]
        read_only_fields = ["psicologo", "fecha_sesion"]

class HistoriaClinicaSerializer(serializers.ModelSerializer):
    evoluciones = EvolucionClinicaSerializer(many=True, read_only=True)

    class Meta:
        model = HistoriaClinica
        fields = [
            "id", "paciente", "fecha_creacion", "antecedentes_familiares", 
            "antecedentes_personales", "diagnostico_preliminar", "evoluciones"
        ]

class PacienteSerializer(serializers.ModelSerializer):
    expediente_id = serializers.ReadOnlyField(source='expediente.id')

    class Meta:
        model = Paciente
        fields = [
            "id", "nombre", "ci", "fecha_nacimiento", 
            "telefono", "motivo_consulta", "expediente_id"
        ]

class PacienteRegistroPublicoSerializer(serializers.Serializer):
    """Serializer para el registro atómico de Paciente + Usuario desde la App Móvil."""
    
    nombre = serializers.CharField(max_length=200)
    ci = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)
    clinica_id = serializers.IntegerField(required=False, allow_null=True)
    fecha_nacimiento = serializers.DateField(required=False, allow_null=True)
    telefono = serializers.CharField(max_length=20)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_clinica_id(self, value):
        if value and not Clinica.objects.filter(id=value).exists():
            raise serializers.ValidationError("La clínica seleccionada no existe.")
        return value

    def create(self, validated_data):
        clinica_id = validated_data.get('clinica_id')
        clinica = None
        if clinica_id:
            clinica = Clinica.objects.get(id=clinica_id)
        
        # 1. Crear el Usuario siempre (Acceso Global)
        user = Usuario.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            clinica=clinica,
            rol='PACIENTE'
        )
        user.first_name = validated_data['nombre']
        user.telefono = validated_data['telefono']
        user.ci = validated_data['ci']
        user.debe_cambiar_password = False
        user.save()
        
        # 2. Si se eligió clínica, crear el registro de Paciente y la Historia Clínica
        if clinica:
            fecha_nac = validated_data.get('fecha_nacimiento') or "2000-01-01"
            paciente = Paciente.objects.create(
                nombre=validated_data['nombre'],
                ci=validated_data['ci'],
                fecha_nacimiento=fecha_nac,
                telefono=validated_data['telefono'],
                clinica=clinica
            )
            HistoriaClinica.objects.create(paciente=paciente)
            return paciente
        
        return user
