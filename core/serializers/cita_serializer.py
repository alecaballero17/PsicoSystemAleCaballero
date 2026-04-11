from rest_framework import serializers
from core.models import Cita


class CitaSerializer(serializers.ModelSerializer):
    """
    Serializer for Cita model, representing appointments.
    Trazabilidad: T005 (Diseño BD) | RF-28 (Control de visibilidad de datos de agenda).
    """

    class Meta:
        model = Cita
        fields = ["id", "paciente", "psicologo", "fecha_hora", "estado"]
