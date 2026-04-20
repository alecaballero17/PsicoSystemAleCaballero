from django.db import models
from apps.P1_Identidad_Acceso.models import Clinica

# ==============================================================================
# MÓDULO: GESTIÓN DE PACIENTES
# ==============================================================================
class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    motivo_consulta = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci})"
