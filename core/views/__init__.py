"""
[SPRINT 1 - T014 / T016 / T017 / T024 / T025] Barrel export de vistas de negocio.
Expone los controladores REST disponibles en el Sprint actual.
"""
# [ALINEACIÓN SPRINT 1 - T016 / RF-28 / RF-29] Vista de métricas por Tenant
from .dashboard_views import DashboardAPIView
# [ALINEACIÓN SPRINT 1 - T014 / RF-02 / CU-02] CRUD de pacientes con aislamiento
from .paciente_views import (
    PacienteListAPIView, 
    PacienteCreateAPIView, 
    PacienteRegistroPublicoAPIView,
    PacienteDeleteAPIView,  # [RF-30] Borrado seguro (Soft Delete)
    AssociateClinicAPIView  # [RF-29] Nueva vinculación para huérfanos
)
# [ALINEACIÓN SPRINT 1 - T024 / T017 / CU-25 / RF-04] Alta de clínicas y usuarios
from .clinica_views import ClinicaCreateAPIView, ClinicaConfigAPIView, UsuarioListCreateAPIView, UsuarioDetailAPIView
# [ALINEACIÓN SPRINT 1 - T025 / CU-24 / RF-29] Gestión de Suscripciones SaaS
from .suscripcion_views import PlanListAPIView, SuscripcionClinicaAPIView, LimitesClinicaAPIView
