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
    password = serializers.CharField(write_only=True, min_length=8)
    clinica_id = serializers.IntegerField()
    fecha_nacimiento = serializers.DateField()
    telefono = serializers.CharField(max_length=20)

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_clinica_id(self, value):
        if not Clinica.objects.filter(id=value).exists():
            raise serializers.ValidationError("La clínica seleccionada no existe.")
        return value

    def create(self, validated_data):
        clinica = Clinica.objects.get(id=validated_data['clinica_id'])
        
        # 1. Crear el Paciente en la Clínica
        paciente = Paciente.objects.create(
            nombre=validated_data['nombre'],
            ci=validated_data['ci'],
            fecha_nacimiento=validated_data['fecha_nacimiento'],
            telefono=validated_data['telefono'],
            clinica=clinica
        )
        
        # 2. Crear el Usuario para acceso móvil (Email como Username)
        user = Usuario.objects.create_user(
            username=validated_data['email'],
            email=validated_data['email'],
            password=validated_data['password'],
            clinica=clinica,
            rol='PACIENTE'
        )
        user.debe_cambiar_password = False
        user.save()
        
        # 3. Crear Historia Clínica automática
        HistoriaClinica.objects.create(paciente=paciente)
        
        return paciente
