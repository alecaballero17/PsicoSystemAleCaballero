from django.db import models
from apps.P1_Identidad_Acceso.models import Clinica, Usuario

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
    fecha_registro = models.DateTimeField(auto_now_add=True, null=True)  # Requerido por ReportePersonalizadoAPIView

    objects = models.Manager()

    def __str__(self):
        return f"{self.nombre} (CI: {self.ci})"

# ==============================================================================
# MÓDULO: HISTORIA CLÍNICA (T026)
# ==============================================================================
class HistoriaClinica(models.Model):
    paciente = models.OneToOneField(Paciente, on_delete=models.CASCADE, related_name='expediente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    antecedentes_familiares = models.TextField(blank=True, default='')
    antecedentes_personales = models.TextField(blank=True, default='')
    diagnostico_preliminar = models.TextField(blank=True, default='')

    def __str__(self):
        return f"Expediente: {self.paciente.nombre}"

class EvolucionClinica(models.Model):
    historia = models.ForeignKey(HistoriaClinica, on_delete=models.CASCADE, related_name='evoluciones')
    psicologo = models.ForeignKey(Usuario, on_delete=models.SET_NULL, null=True)
    fecha_sesion = models.DateTimeField(auto_now_add=True)
    notas_sesion = models.TextField()
    archivo_adjunto = models.FileField(upload_to='historias/adjuntos/', null=True, blank=True)
    
    # Campo para el Diagnóstico Predictivo de IA (IA-01)
    analisis_ia = models.TextField(blank=True, default='', help_text="Resultado del análisis predictivo de IA")

    def __str__(self):
        return f"Sesión {self.fecha_sesion} - {self.historia.paciente.nombre}"
