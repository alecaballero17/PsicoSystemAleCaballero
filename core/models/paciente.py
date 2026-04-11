from django.db import models
from .clinica import Clinica  # <-- IMPORTACIÓN CLAVE


# ==============================================================================
# MÓDULO: GESTIÓN DE PACIENTES
# [SPRINT 0 - T005] Modelado de Datos: Entidad Paciente con aislamiento por clínica.
# Nota: Los endpoints CRUD (T013, T014) corresponden a Sprint 1.
# ==============================================================================
class Paciente(models.Model):
    """
    Representa a los pacientes atendidos.
    Los datos están segregados por clínica (RF-29).
    """

    # [SPRINT 0 - T005] Garantiza que un psicólogo de la Clínica A no vea pacientes de la Clínica B.
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, db_index=True)  # [SPRINT 0 - T005] FK Multi-tenant

    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True, db_index=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    motivo_consulta = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci})"
