from django.db import models
from django.conf import settings
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver

class LogAuditoria(models.Model):
    usuario = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    accion = models.CharField(max_length=255)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']

    def __str__(self):
        return f"[{self.fecha.strftime('%Y-%m-%d %H:%M')}] {self.usuario} - {self.accion}"

# Señales automáticas para Login y Logout
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    LogAuditoria.objects.create(usuario=user, accion="Inició sesión en el sistema.")

@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    if user:
        LogAuditoria.objects.create(usuario=user, accion="Cerró sesión a través del portal web.")

# ==============================================================================
# T056/T058: Módulo Financiero
# ==============================================================================
class Transaccion(models.Model):
    clinica = models.ForeignKey('P1_Identidad_Acceso.Clinica', on_delete=models.CASCADE)
    paciente = models.ForeignKey('P2_Gestion_Clinica.Paciente', on_delete=models.CASCADE)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha = models.DateTimeField(auto_now_add=True)
    concepto = models.CharField(max_length=255)
    
    METODOS_PAGO = [
        ('EFECTIVO', 'Efectivo'),
        ('TRANSFERENCIA', 'Transferencia'),
        ('QR', 'QR / Pago Móvil'),
    ]
    metodo_pago = models.CharField(max_length=20, choices=METODOS_PAGO, default='EFECTIVO')

    class Meta:
        verbose_name = "Transacción"
        verbose_name_plural = "Transacciones"

class Comprobante(models.Model):
    transaccion = models.OneToOneField(Transaccion, on_delete=models.CASCADE)
    nro_comprobante = models.CharField(max_length=50, unique=True)
    pdf_archivo = models.FileField(upload_to='comprobantes/pdf/', null=True, blank=True)
    fecha_emision = models.DateTimeField(auto_now_add=True)

# ==============================================================================
# IA: Analítica Médica (Docente)
# ==============================================================================
class DiagnosticoIA(models.Model):
    paciente = models.ForeignKey('P2_Gestion_Clinica.Paciente', on_delete=models.CASCADE, null=True, blank=True)
    psicologo = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    input_clinico = models.TextField(help_text="Notas clínicas base para el diagnóstico")
    resultado_ia = models.TextField()
    probabilidad_acierto = models.FloatField(default=0.0)
    fecha_analisis = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Diagnóstico IA"
        verbose_name_plural = "Diagnósticos IA"

