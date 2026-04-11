from django.contrib import admin
from core.models import Clinica


@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "nit", "plan_suscripcion")
