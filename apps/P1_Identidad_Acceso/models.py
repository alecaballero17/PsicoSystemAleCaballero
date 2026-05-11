from django.db import models
from django.contrib.auth.models import AbstractUser

# ==============================================================================
# MÓDULO: GESTIÓN ORGANIZACIONAL (TENANT)
# ==============================================================================
class Clinica(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()

    PLANES = [
        ('Basico', 'Básico'),
        ('Profesional', 'Profesional'),
        ('Premium', 'Premium'),
    ]
    plan_suscripcion = models.CharField(max_length=50, choices=PLANES, default='Basico')

    def __str__(self):
        return str(self.nombre)

# ==============================================================================
# MÓDULO: SEGURIDAD Y ACCESO (USUARIOS)
# ==============================================================================
class Usuario(AbstractUser):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, null=True, blank=True)

    ROLES = [
        ('ADMIN', 'Administrador'),
        ('PSICOLOGO', 'Psicólogo'),
        ('PACIENTE', 'Paciente')
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='PSICOLOGO')
    especialidad = models.CharField(max_length=100, blank=True, default='')
    telefono = models.CharField(max_length=20, blank=True, default='')

    # Seguridad: Requerimientos del docente
    ultima_fecha_pass = models.DateTimeField(auto_now_add=True)
    forzar_cambio_pass = models.BooleanField(default=False)
