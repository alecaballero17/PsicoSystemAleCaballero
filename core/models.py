from django.db import models
from django.contrib.auth.models import AbstractUser

# Módulo de Gestión Organizacional (El Tenant)
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
        return self.nombre

# Extendemos el usuario para que pertenezca a una clínica
class Usuario(AbstractUser):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, null=True, blank=True)
    # VERIFICA QUE ESTA LÍNEA EXISTA:
    rol = models.CharField(max_length=20, choices=[
        ('ADMIN', 'Administrador'),
        ('PSICOLOGO', 'Psicólogo'),
        ('PACIENTE', 'Paciente')
    ], default='PSICOLOGO')

# Módulo de Gestión de Pacientes (Aislado por clínica)
class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100) # <--- Verifica que se llame 'nombre'
    ci = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    telefono = models.CharField(max_length=20) # <--- Verifica que se llame 'telefono'
    motivo_consulta = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.nombre