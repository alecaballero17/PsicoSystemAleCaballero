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

    nombre = models.CharField(max_length=100)  # [SPRINT 0 - T005] Campo base del tenant
    nit = models.CharField(max_length=20, unique=True)  # [SPRINT 0 - T005] Identificador único fiscal
    direccion = models.TextField()  # [SPRINT 0 - T005] Ubicación física de la clínica

    # ---------------------------------------------------------
    # CORRECCIÓN CAUSA RAÍZ #3: AGREGAMOS LOS CAMPOS FALTANTES
    # ---------------------------------------------------------
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email_contacto = models.EmailField(blank=True, null=True)

    # RNF-01 (Escalabilidad): Soporte para diferentes niveles de servicio.
    PLANES = [
        ("Basico", "Básico"),
        ("Profesional", "Profesional"),
        ("Premium", "Premium"),
    ]
    plan_suscripcion = models.CharField(max_length=50, choices=PLANES, default="Basico")

    def __str__(self):
        return str(self.nombre)
