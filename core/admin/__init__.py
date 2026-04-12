"""
[SPRINT 0] Módulo de administración principal.
Exporta las configuraciones de ModelAdmin de cada dominio para su registro en el panel de Django.
"""

from .admin_clinica import ClinicaAdmin
from .admin_usuario import UsuarioAdmin
from .admin_paciente import PacienteAdmin, CitaAdmin

__all__ = [
    "ClinicaAdmin",
    "UsuarioAdmin",
    "PacienteAdmin",
    "CitaAdmin",
]
