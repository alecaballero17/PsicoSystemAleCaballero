from django.db import models
from apps.P1_Identidad_Acceso.models import Clinica

# ==============================================================================
# MÓDULO: GESTIÓN DE PACIENTES
# ==============================================================================
class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)

    nombre = models.CharField(max_length=100)
    ci = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20)
    motivo_consulta = models.TextField(null=True, blank=True)

    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci})"

# ==============================================================================
# T026: API de Expediente Clínico
# ==============================================================================
class ExpedienteClinico(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='expediente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    ultima_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Expediente Clínico"
        verbose_name_plural = "Expedientes Clínicos"

    def __str__(self):
        return f"Expediente de {self.paciente.nombre}"

class NotaClinica(models.Model):
    expediente = models.ForeignKey(ExpedienteClinico, on_delete=models.CASCADE, related_name='notas')
    psicologo = models.ForeignKey('P1_Identidad_Acceso.Usuario', on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Nota Clínica"
        verbose_name_plural = "Notas Clínicas"
        ordering = ['-fecha']

class ArchivoAdjunto(models.Model):
    expediente = models.ForeignKey(ExpedienteClinico, on_delete=models.CASCADE, related_name='archivos')
    archivo = models.FileField(upload_to='expedientes/archivos/')
    descripcion = models.CharField(max_length=255, blank=True)
    fecha_subida = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Archivo Adjunto"
        verbose_name_plural = "Archivos Adjuntos"

# ==============================================================================
# T060/T061 SPRINT 4: Historial Clínico y Evoluciones (CU29)
# ==============================================================================
class DiagnosticoPaciente(models.Model):
    """Diagnóstico global del tratamiento: inicial y final con fechas."""
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='diagnostico_global')
    psicologo = models.ForeignKey('P1_Identidad_Acceso.Usuario', on_delete=models.CASCADE)
    diagnostico_inicial = models.TextField(help_text="Diagnóstico al inicio del tratamiento")
    fecha_inicio = models.DateField(help_text="Fecha de inicio del tratamiento")
    diagnostico_final = models.TextField(blank=True, default='', help_text="Diagnóstico al cierre del tratamiento")
    fecha_fin = models.DateField(null=True, blank=True, help_text="Fecha de cierre del tratamiento")

    ESTADOS_TRATAMIENTO = [
        ('EN_TRATAMIENTO', 'En tratamiento'),
        ('ALTA', 'Alta'),
        ('ABANDONO', 'Abandono'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS_TRATAMIENTO, default='EN_TRATAMIENTO')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Diagnóstico del Paciente"
        verbose_name_plural = "Diagnósticos de Pacientes"

    def __str__(self):
        return f"Diagnóstico de {self.paciente.nombre} ({self.get_estado_display()})"

class Evolucion(models.Model):
    """Nota de evolución por sesión/cita con recomendación del psicólogo."""
    paciente = models.ForeignKey(Paciente, on_delete=models.CASCADE, related_name='evoluciones')
    psicologo = models.ForeignKey('P1_Identidad_Acceso.Usuario', on_delete=models.CASCADE)
    cita = models.ForeignKey('P3_Logistica_Citas.Cita', on_delete=models.SET_NULL, null=True, blank=True, related_name='evoluciones')
    fecha_sesion = models.DateField(help_text="Fecha de la sesión clínica")
    diagnostico = models.TextField(help_text="Diagnóstico de esta sesión")
    observaciones = models.TextField(blank=True, default='', help_text="Observaciones generales de la sesión")

    ESTADOS_ANIMO = [
        ('BUENO', 'Bueno'),
        ('REGULAR', 'Regular'),
        ('MALO', 'Malo'),
        ('CRITICO', 'Crítico'),
    ]
    estado_animo = models.CharField(max_length=10, choices=ESTADOS_ANIMO, default='REGULAR')
    recomendacion = models.TextField(blank=True, default='', help_text="Recomendación del psicólogo al paciente para esta sesión")
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Evolución Clínica"
        verbose_name_plural = "Evoluciones Clínicas"
        ordering = ['-fecha_sesion']

    def __str__(self):
        return f"Evolución de {self.paciente.nombre} - {self.fecha_sesion}"
