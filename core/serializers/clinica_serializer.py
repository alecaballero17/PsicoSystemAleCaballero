"""
[SPRINT 1 - T024] Registro de Clínica (Tenant): Serialización del modelo organizacional.
[RF-29] Aislamiento SaaS: Expone los campos necesarios para el alta de un nuevo Tenant.
[CU-25] Registro de Nuevas Clínicas: Motor de validación del formulario de alta.
"""
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
            "logo_url",
            "plan_suscripcion",
        ]
        read_only_fields = ["id"]
