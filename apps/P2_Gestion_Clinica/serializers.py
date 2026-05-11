from rest_framework import serializers
from .models import Paciente, ExpedienteClinico, NotaClinica, ArchivoAdjunto

class PacienteSerializer(serializers.ModelSerializer):
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

class NotaClinicaSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')

    class Meta:
        model = NotaClinica
        fields = ['id', 'psicologo', 'psicologo_nombre', 'contenido', 'fecha']

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoAdjunto
        fields = ['id', 'archivo', 'descripcion', 'fecha_subida']

class ExpedienteClinicoSerializer(serializers.ModelSerializer):
    notas = NotaClinicaSerializer(many=True, read_only=True)
    archivos = ArchivoAdjuntoSerializer(many=True, read_only=True)
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')

    class Meta:
        model = ExpedienteClinico
        fields = ['id', 'paciente', 'paciente_nombre', 'fecha_creacion', 'ultima_actualizacion', 'notas', 'archivos']

class PacienteDetalleSerializer(serializers.ModelSerializer):
    expediente = ExpedienteClinicoSerializer(read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'
