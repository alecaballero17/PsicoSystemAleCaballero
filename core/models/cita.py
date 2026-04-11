from django.db import models
from .paciente import Paciente  # <-- IMPORTACIÓN CLAVE
from .usuario import Usuario  # <-- IMPORTACIÓN CLAVE


# ==============================================================================
# MÓDULO: GESTIÓN DE CITAS
# [SPRINT 0 - T005] Diseño de BD Inicial: Completa el esquema relacional básico.
# Nota: La lógica de negocio de citas corresponde a Sprints futuros.
# ==============================================================================
class Cita(models.Model):
    """
    Entidad para la programación de sesiones.
    Completa el esquema relacional básico solicitado en el Sprint 0.
    """

    # Relación uno a muchos: Un paciente puede tener múltiples citas.
    paciente = models.ForeignKey(
        Paciente, on_delete=models.CASCADE, related_name="citas"
    )

    # Restricción de integridad: Solo usuarios con rol PSICOLOGO pueden atender citas.
    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={"rol": "PSICOLOGO"},
        related_name="citas_asignadas",
    )

    fecha_hora = models.DateTimeField(help_text="RNF-05: Precisión temporal en citas")
    motivo = models.TextField(blank=True, null=True)

    # Estados de flujo para trazabilidad de la consulta.
    ESTADOS = [
        ("PENDIENTE", "Pendiente"),
        ("COMPLETADA", "Completada"),
        ("CANCELADA", "Cancelada"),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default="PENDIENTE")

    objects = models.Manager()

    class Meta:
        """Metadatos de la clase Cita."""

        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        # Mejora: Ordenar por fecha por defecto
        ordering = ["fecha_hora"]

    def __str__(self):
        return f"Cita: {self.paciente} con {self.psicologo} - {self.fecha_hora}"
