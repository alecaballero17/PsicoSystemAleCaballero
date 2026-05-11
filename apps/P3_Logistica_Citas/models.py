from django.db import models
from django.core.exceptions import ValidationError
from datetime import timedelta
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
    duracion_minutos = models.PositiveIntegerField(default=60, help_text="Duración estimada de la cita")
    motivo = models.TextField(blank=True, null=True)

    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('ASISTIO', 'Asistió'),
        ('NO_ASISTIO', 'No asistió'),
        ('CANCELADA', 'Cancelada'),
        ('REPROGRAMADA', 'Reprogramada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    objects = models.Manager()

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha_hora']

    def clean(self):
        # T030: Validación de disponibilidad (Choque de horarios)
        inicio = self.fecha_hora
        fin = self.fecha_hora + timedelta(minutes=self.duracion_minutos)
        
        citas_traslapadas = Cita.objects.filter(
            psicologo=self.psicologo,
            estado__in=['PENDIENTE', 'ASISTIO']
        ).filter(
            models.Q(fecha_hora__lt=fin, fecha_hora__gte=inicio) |
            models.Q(fecha_hora__lte=inicio, fecha_hora__gt=inicio - timedelta(minutes=60)) # Simplificado a 60 min si no hay fin guardado
        ).exclude(pk=self.pk)

        if citas_traslapadas.exists():
            raise ValidationError(f"El psicólogo {self.psicologo.get_full_name()} ya tiene una cita programada en este horario.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Cita: {self.paciente} con {self.psicologo} - {self.fecha_hora}"

# ==============================================================================
# T031: Gestión de Lista de Espera
# ==============================================================================
class ListaEspera(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE)
    clinica = models.ForeignKey('P1_Identidad_Acceso.Clinica', on_delete=models.CASCADE)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    prioridad = models.PositiveIntegerField(default=1)
    notas = models.TextField(blank=True)

    class Meta:
        verbose_name = "Lista de Espera"
        verbose_name_plural = "Listas de Espera"
        ordering = ['-prioridad', 'fecha_registro']
