from django.contrib import admin
from .models import Clinica, Usuario

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'plan_suscripcion')
    search_fields = ('nombre', 'nit')
    list_filter = ('plan_suscripcion',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'rol', 'clinica')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'clinica')
