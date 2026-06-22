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
        ('NO_ASISTIO', 'No Asistió'),  # T032: Control de Asistencia
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    ESTADOS_PAGO = [
        ('PENDIENTE', 'Pago Pendiente'),
        ('PAGADO', 'Pagado'),
    ]
    estado_pago = models.CharField(max_length=20, choices=ESTADOS_PAGO, default='PENDIENTE')
    monto = models.DecimalField(max_digits=10, decimal_places=2, default=120.00)
    
    # Nuevos campos para la gestión de citas desde la app
    numero_ficha = models.CharField(max_length=20, unique=True, blank=True, null=True)
    codigo_qr = models.TextField(blank=True, null=True, help_text="Datos para generar QR en frontend")
    duracion_minutos = models.IntegerField(default=60)

    objects = models.Manager()

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['fecha_hora']

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        
        # Generar numero de ficha si es nuevo
        if is_new and not self.numero_ficha:
            self.numero_ficha = f"FICHA-{self.pk:05d}"
            # El QR guardará la data estructurada de la cita
            self.codigo_qr = f"CITA:{self.pk}|FICHA:{self.numero_ficha}|PAC:{self.paciente.ci}"
            self.save(update_fields=['numero_ficha', 'codigo_qr'])

    def __str__(self):
        return f"Cita: {self.paciente} con {self.psicologo} - {self.fecha_hora}"

# ==============================================================================
# MÓDULO: LISTA DE ESPERA (T031)
# ==============================================================================
class ListaEspera(models.Model):
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='esperas')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    prioridad = models.IntegerField(default=1) # 1: Alta, 2: Media, 3: Baja
    observacion = models.TextField(blank=True)
    activo = models.BooleanField(default=True)

    class Meta:
        ordering = ['prioridad', 'fecha_registro']

    def __str__(self):
        return f"Espera: {self.paciente.nombre} (Prio: {self.prioridad})"
