"""
Administración de la entidad Clínica.
"""

from django.contrib import admin
from core.models import Clinica


@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    """
    Configuración de la interfaz de administración para el modelo Clínica.
    """

    list_display = ("nombre", "nit", "plan_suscripcion")
