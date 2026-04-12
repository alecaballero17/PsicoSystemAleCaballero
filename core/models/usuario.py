"""
Módulo de modelo para la entidad Usuario (RBAC) en PsicoSystem SI2.
[SPRINT 0 - T005] Gestión de accesos y roles.
"""

from django.db import models
from django.contrib.auth.models import AbstractUser
from .clinica import Clinica  # <-- IMPORTACIÓN CLAVE


# ==============================================================================
# MÓDULO: SEGURIDAD Y ACCESO (USUARIOS)
# [SPRINT 0 - T005] Modelado de Datos Multi-tenant: Usuario extendido con roles y clínica.
# [RNF-03] Control de identidad con RBAC para restricción de acceso.
# ==============================================================================
class Usuario(AbstractUser):
    """
    Extensión del usuario base de Django para soportar Multi-tenancy y Roles.
    Vinculado a RNF-03 (Seguridad de Identidad).
    """

    # [SPRINT 0 - T005] FK hacia Clinica: Implementa el aislamiento lógico del usuario.
    clinica = models.ForeignKey(
        Clinica,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        db_index=True,
        help_text="Clínica obligatoria para la segregación de datos (RF-29). Opcional para pacientes huérfanos.",
    )

    # [SPRINT 0 - T005] Control de acceso basado en roles para la lógica de negocio.
    ROLES = [
        ("ADMIN", "Administrador"),
        ("PSICOLOGO", "Psicólogo"),
        ("PACIENTE", "Paciente"),
        ("RECEPCIONISTA", "Recepcionista"),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default="PSICOLOGO")

    # [SPRINT 1 - CU-05] Cierre de brecha administrativa. Metadata básica de personal.
    especialidad = models.CharField(
        max_length=150, 
        null=True, 
        blank=True, 
        help_text="Especialidad clínica (ej. Psicología Infantil)"
    )
    horario_atencion = models.TextField(
        null=True, 
        blank=True, 
        help_text="Horario de atención en formato texto libre"
    )

