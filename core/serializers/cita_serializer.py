"""
[SPRINT 0 - T005] Modelo de Cita creado en el diseño del esquema ER.
[ALCANCE-POSTERIOR - SPRINT 2] La lógica de CRUD de citas (endpoints, vistas, UI) pertenece
al Sprint 2 (Módulo Agenda). Este serializador se conserva pero no se expone a través de URLs.
"""
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
