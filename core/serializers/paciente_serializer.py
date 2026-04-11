from rest_framework import serializers
from core.models import Paciente


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
        ]
