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
    es_psicologo = models.BooleanField(default=False)

# Módulo de Gestión de Pacientes (Aislado por clínica)
class Paciente(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE) # Esto hace que sea Multi-tenant
    nombre_completo = models.CharField(max_length=200)
    ci = models.CharField(max_length=15)
    fecha_nacimiento = models.DateField()
    historia_clinica_nro = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"{self.nombre_completo} - {self.clinica.nombre}"