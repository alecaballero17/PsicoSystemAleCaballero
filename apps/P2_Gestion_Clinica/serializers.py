from rest_framework import serializers
from .models import Paciente, ExpedienteClinico, NotaClinica, ArchivoAdjunto, Evolucion, DiagnosticoPaciente

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

# ==============================================================================
# SPRINT 4: Serializers de Evolución y Diagnóstico (CU29)
# ==============================================================================
class EvolucionSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')
    estado_animo_display = serializers.ReadOnlyField(source='get_estado_animo_display')

    class Meta:
        model = Evolucion
        fields = [
            'id', 'paciente', 'psicologo', 'psicologo_nombre',
            'cita', 'fecha_sesion', 'diagnostico', 'observaciones',
            'estado_animo', 'estado_animo_display',
            'recomendacion', 'fecha_creacion'
        ]
        read_only_fields = ['psicologo']

class DiagnosticoPacienteSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')
    estado_display = serializers.ReadOnlyField(source='get_estado_display')

    class Meta:
        model = DiagnosticoPaciente
        fields = [
            'id', 'paciente', 'psicologo', 'psicologo_nombre',
            'diagnostico_inicial', 'fecha_inicio',
            'diagnostico_final', 'fecha_fin',
            'estado', 'estado_display', 'fecha_creacion'
        ]
        read_only_fields = ['psicologo']

class PacienteDetalleSerializer(serializers.ModelSerializer):
    expediente = ExpedienteClinicoSerializer(read_only=True)
    diagnostico_global = DiagnosticoPacienteSerializer(read_only=True)
    evoluciones = EvolucionSerializer(many=True, read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'
