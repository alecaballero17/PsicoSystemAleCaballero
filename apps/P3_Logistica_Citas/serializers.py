from rest_framework import serializers

from .models import Cita, ListaEspera


class CitaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')

    class Meta:
        model = Cita
        fields = ["id", "paciente", "paciente_nombre", "psicologo", "psicologo_nombre", "fecha_hora", "duracion_minutos", "motivo", "estado"]

    def validate(self, attrs):
        # ... (rest of the existing validation logic)
        return attrs

class ListaEsperaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')

    class Meta:
        model = ListaEspera
        fields = '__all__'
