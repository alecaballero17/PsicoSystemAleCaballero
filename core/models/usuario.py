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
        on_delete=models.CASCADE,
        null=True,
        blank=False,  # <--- CORRECCIÓN: Obliga a elegir una clínica en el Admin
        db_index=True,
        help_text="Clínica obligatoria para la segregación de datos (RF-29)",
    )

    # [SPRINT 0 - T005] Control de acceso basado en roles para la lógica de negocio.
    ROLES = [
        ("ADMIN", "Administrador"),
        ("PSICOLOGO", "Psicólogo"),
        ("PACIENTE", "Paciente"),
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default="PSICOLOGO")
