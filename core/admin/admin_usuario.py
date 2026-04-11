from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from core.models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("PsicoSystem Info", {"fields": ("clinica", "rol")}),
    )
    list_display = ("username", "email", "clinica", "rol")
