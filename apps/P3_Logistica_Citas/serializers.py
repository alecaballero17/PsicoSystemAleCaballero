from rest_framework import serializers

from .models import Cita, ListaEspera


class CitaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')

    class Meta:
        model = Cita
        fields = ["id", "paciente", "paciente_nombre", "psicologo", "psicologo_nombre", "fecha_hora", "duracion_minutos", "motivo", "estado"]

    def validate(self, attrs):
        fecha_hora = attrs.get('fecha_hora')
        psicologo = attrs.get('psicologo')
        
        # T038: Validación de Disponibilidad (Control de horarios)
        # Buscar citas del mismo psicólogo que se traslapen
        qs = Cita.objects.filter(psicologo=psicologo, fecha_hora=fecha_hora).exclude(estado='CANCELADA')
        if self.instance:
            qs = qs.exclude(pk=self.instance.pk)
            
        if qs.exists():
            raise serializers.ValidationError("Advertencia: El psicólogo ya tiene una cita programada en este horario.")
            
        return attrs

class ListaEsperaSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')

    class Meta:
        model = ListaEspera
        fields = '__all__'
