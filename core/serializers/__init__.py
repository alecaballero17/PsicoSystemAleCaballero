"""
[SPRINT 1] Módulo de serializadores principales.
Expecta los serializadores de DRF para su uso a nivel de paquete en la API.
"""

from .clinica_serializer import ClinicaSerializer      # [SPRINT 1 - T024] Alta de Tenant
from .usuario_serializer import UsuarioSerializer      # [SPRINT 1 - T017] CRUD Psicólogos
from .paciente_serializer import PacienteSerializer    # [SPRINT 1 - T014] Registro de Pacientes
# [ALCANCE-POSTERIOR] CitaSerializer pertenece al Sprint 2 (Módulo Agenda).
# El modelo Cita existe desde Sprint 0 - T005 (diseño ER), pero los endpoints
# REST de citas no forman parte del cronograma actual. Se preserva el código.
# from .cita_serializer import CitaSerializer

__all__ = [
    "ClinicaSerializer",
    "UsuarioSerializer",
    "PacienteSerializer",
    # "CitaSerializer",  # [ALCANCE-POSTERIOR] Habilitado en Sprint 2
]
