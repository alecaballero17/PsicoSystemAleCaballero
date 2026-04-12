"""
Modelo de Suscripción para el sistema Multi-tenant de PsicoSystem SI2.
[SPRINT 1 - T025] Gestión de Planes y Suscripciones SaaS (CU-24).
"""

from django.db import models
from core.models.clinica import Clinica


class PlanSuscripcion(models.Model):
    """[SPRINT 1 - T025] [CU-24] Define un plan de suscripción SaaS."""

    PLANES = [
        ("BASIC", "Plan Básico"),
        ("PRO", "Plan Profesional"),
        ("PREMIUM", "Plan Premium"),
    ]

    nombre = models.CharField(max_length=20, choices=PLANES, unique=True)
    descripcion = models.TextField(blank=True)
    max_pacientes = models.IntegerField(
        default=50,
        help_text="Límite máximo de pacientes por clínica en este plan.",
    )
    max_psicologos = models.IntegerField(
        default=3,
        help_text="Límite máximo de psicólogos por clínica en este plan.",
    )
    precio_mensual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Precio en USD por mes.",
    )
    activo = models.BooleanField(default=True)

    objects = models.Manager()

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadatos de PlanSuscripcion."""

        verbose_name = "Plan de Suscripción"
        verbose_name_plural = "Planes de Suscripción"

    def __str__(self):
        # get_nombre_display() es generado dinámicamente por Django para campos con choices
        return (
            f"{self.get_nombre_display()} - "  # pylint: disable=no-member
            f"${self.precio_mensual}/mes"
        )


class Suscripcion(models.Model):
    """[SPRINT 1 - T025] [CU-24] Vincula una clínica a un plan activo."""

    ESTADOS = [
        ("ACTIVA", "Activa"),
        ("SUSPENDIDA", "Suspendida"),
        ("CANCELADA", "Cancelada"),
        ("TRIAL", "Período de Prueba"),
    ]

    clinica = models.OneToOneField(
        Clinica,
        on_delete=models.CASCADE,
        related_name="suscripcion",
        help_text="[RF-29] Cada clínica tiene exactamente una suscripción.",
    )
    plan = models.ForeignKey(
        PlanSuscripcion,
        on_delete=models.PROTECT,
        help_text="Plan al que está suscrita la clínica.",
    )
    estado = models.CharField(max_length=15, choices=ESTADOS, default="TRIAL")
    fecha_inicio = models.DateField(auto_now_add=True)
    fecha_fin = models.DateField(
        null=True,
        blank=True,
        help_text="Fecha de expiración de la suscripción.",
    )

    objects = models.Manager()

    class Meta:  # pylint: disable=too-few-public-methods
        """Metadatos de Suscripcion."""

        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"

    def __str__(self):
        # .nombre es accesible en runtime vía el descriptor de Django
        return (
            f"{self.clinica.nombre} → "  # pylint: disable=no-member
            f"{self.plan.nombre} ({self.estado})"  # pylint: disable=no-member
        )

    def esta_activa(self):
        """Verifica si la suscripción está vigente."""
        return self.estado in ["ACTIVA", "TRIAL"]
