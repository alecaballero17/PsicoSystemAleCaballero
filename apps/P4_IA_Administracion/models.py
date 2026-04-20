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

