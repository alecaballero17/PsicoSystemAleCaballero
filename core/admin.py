"""
Configuración de la interfaz de administración de administración de PsicoSystem.
"""
from django.contrib import admin
from .models import Clinica, Usuario, Paciente, Cita

admin.site.register(Clinica)
admin.site.register(Usuario)
admin.site.register(Paciente)
admin.site.register(Cita)
