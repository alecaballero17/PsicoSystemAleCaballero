"""
Módulo de modelo para la entidad Clínica (Tenant) en PsicoSystem SI2.
[SPRINT 0 - T005] Persistencia organizacional.
"""

from django.db import models


# ==============================================================================
# MÓDULO: GESTIÓN ORGANIZACIONAL (TENANT)
# [SPRINT 0 - T005] Modelado de Datos Multi-tenant: Entidad raíz para aislamiento lógico.
# [RNF-03] Los datos se segregan por clínica para garantizar control de acceso.
# ==============================================================================
class Clinica(models.Model):
    """
    Entidad raíz para el aislamiento de datos.
    Representa a cada consultorio o clínica que contrata el SaaS.
    """

    # [SPRINT 0 - T005] Campo base del tenant
    nombre = models.CharField(max_length=100)
    # [SPRINT 0 - T005] Identificador único fiscal
    nit = models.CharField(max_length=20, unique=True)
    # [SPRINT 0 - T005] Ubicación física de la clínica
    direccion = models.TextField()

    # ---------------------------------------------------------
    # CORRECCIÓN CAUSA RAÍZ #3: AGREGAMOS LOS CAMPOS FALTANTES
    # ---------------------------------------------------------
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)
    # [SPRINT 1 - RF-29] URL del Logotipo de la Institución
    logo_url = models.URLField(max_length=500, blank=True, null=True, help_text="Logo Institucional (Tenant)")

    # RNF-01 (Escalabilidad): Soporte para diferentes niveles de servicio.
    PLANES = [
        ("Basico", "Básico"),
        ("Profesional", "Profesional"),
        ("Premium", "Premium"),
    ]
    plan_suscripcion = models.CharField(max_length=50, choices=PLANES, default="Basico")

    objects = models.Manager()

    def __str__(self):
        return str(self.nombre)
