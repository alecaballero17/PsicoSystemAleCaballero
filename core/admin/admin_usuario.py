"""
Administración de la entidad Usuario.
Personaliza el UserAdmin de Django para las necesidades de PsicoSystem.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    """
    Configuración de la interfaz de administración para el modelo Usuario.
    Extiende el UserAdmin estándar para incorporar 'clinica' y 'rol'.
    """

    fieldsets = UserAdmin.fieldsets + (
        ("PsicoSystem Info", {"fields": ("clinica", "rol")}),
    )
    list_display = ("username", "email", "clinica", "rol")
