from django.contrib import admin
from .models import Clinica, Usuario

from django.contrib.auth.admin import UserAdmin

@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nit', 'plan_suscripcion')
    search_fields = ('nombre', 'nit')
    list_filter = ('plan_suscripcion',)

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ('username', 'email', 'rol', 'clinica', 'is_staff')
    search_fields = ('username', 'email')
    list_filter = ('rol', 'clinica', 'is_staff', 'is_superuser')
    
    fieldsets = UserAdmin.fieldsets + (
        ('Información de la Clínica y Rol', {'fields': ('clinica', 'rol', 'especialidad', 'telefono', 'ci')}),
        ('Métricas y Seguridad', {'fields': ('cancelaciones_hoy', 'ultima_cancelacion_fecha', 'ultimo_cambio_password', 'debe_cambiar_password')}),
    )
