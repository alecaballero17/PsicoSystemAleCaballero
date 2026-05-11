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
