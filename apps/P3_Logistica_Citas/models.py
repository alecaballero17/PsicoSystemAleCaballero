from django.db import models
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P1_Identidad_Acceso.models import Usuario

# ==============================================================================
# MÓDULO: GESTIÓN DE CITAS
# ==============================================================================
class Cita(models.Model):
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='citas'
    )

    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'PSICOLOGO'},
        related_name='citas_asignadas'
    )

    fecha_hora = models.DateTimeField(help_text="RNF-05: Precisión temporal en citas")
    motivo = models.TextField(blank=True, null=True)

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    objects = models.Manager()

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Cita: {self.paciente} con {self.psicologo} - {self.fecha_hora}"
