from rest_framework import serializers
from .models import Paciente, HistoriaClinica, EvolucionClinica

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
