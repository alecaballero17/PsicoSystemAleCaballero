"""
Módulo de modelo para la entidad Paciente en PsicoSystem SI2.
[SPRINT 0 - T005] Gestión de ficha clínica.
"""

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

    # [SPRINT 0 - T005] Garantiza que un psicólogo de la Clínica A
    # no vea pacientes de la Clínica B.
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
    )  # [SPRINT 0 - T005] FK Multi-tenant (Opcional para pacientes huérfanos)

    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True, db_index=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True, db_index=True)
    motivo_consulta = models.TextField(null=True, blank=True)
    
    # [ALINEACIÓN RF-30] Borrado Lógico: Garantiza integridad para auditorías.
    activo = models.BooleanField(default=True, db_index=True)
    
    # Origen del registro para saber si fue por la App Móvil o Web
    ORIGEN_CHOICES = [
        ('WEB', 'Web'),
        ('MOVIL', 'Móvil'),
    ]
    origen = models.CharField(max_length=10, choices=ORIGEN_CHOICES, default='WEB')

    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci})"
