from rest_framework import serializers
from core.models import Clinica


class ClinicaSerializer(serializers.ModelSerializer):
    """
    Serializer for Clinica model. Maps Clinica fields to JSON representation.
    Trazabilidad: CU-25 (Registrar Clínica).
    Convierte el modelo Clinica a JSON para la API de administración.
    """

    class Meta:
        model = Clinica
        fields = [
            "id",
            "nombre",
            "nit",
            "direccion",
            "telefono",
            "email_contacto",
            "plan_suscripcion",
        ]
        read_only_fields = ["id"]
