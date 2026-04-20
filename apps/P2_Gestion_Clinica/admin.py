from django.contrib import admin
from .models import Paciente

@admin.register(Paciente)
class PacienteAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'ci', 'telefono', 'clinica')
    search_fields = ('nombre', 'ci')
    list_filter = ('clinica',)
