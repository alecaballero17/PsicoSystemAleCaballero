"""
Administración de las entidades Paciente y Cita.
"""

from django.contrib import admin
from core.models import Paciente, Cita


@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz de administración para el modelo Paciente.
    """

    list_display = ("nombre", "ci", "clinica", "telefono")
    search_fields = ("nombre", "ci")
    list_filter = ("clinica",)


@admin.register(Cita)
class CitaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz de administración para el modelo Cita.
    """

    list_display = ("paciente", "psicologo", "fecha_hora", "estado")
    list_filter = ("estado", "fecha_hora")
