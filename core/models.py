"""
Módulo de modelos principales del sistema (core).
Incluye las definiciones de Clínica, Usuario, Paciente y Cita.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser

# ==============================================================================
# MÓDULO: GESTIÓN ORGANIZACIONAL (TENANT)
# TRAZABILIDAD: RF-29 (Multi-tenancy) | SPRINT 0 (T005)
# ==============================================================================
class Clinica(models.Model):
    """
    Entidad raíz para el aislamiento de datos. 
    Representa a cada consultorio o clínica que contrata el SaaS.
    """
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()

    # RNF-01 (Escalabilidad): Soporte para diferentes niveles de servicio.
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
# TRAZABILIDAD: RF-01 (JWT) | RF-28 (Roles) | CU-01 (Login) | SPRINT 0 (T005)
# ==============================================================================
class Usuario(AbstractUser):
    """
    Extensión del usuario base de Django para soportar Multi-tenancy y Roles.
    Vinculado a RNF-03 (Seguridad de Identidad).
    """
    # FK hacia Clinica: Implementa el aislamiento lógico del usuario.
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, null=True, blank=True)

    # RF-28: Control de acceso basado en roles para la lógica de negocio.
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('PSICOLOGO', 'Psicólogo'),
        ('PACIENTE', 'Paciente')
    ]
    rol = models.CharField(max_length=20, choices=ROLES, default='PSICOLOGO')

# ==============================================================================
# MÓDULO: GESTIÓN DE PACIENTES
# TRAZABILIDAD: RF-02 (Registro) | CU-02 | SPRINT 1 (T013, T014)
# ==============================================================================
class Paciente(models.Model):
    """
    Representa a los pacientes atendidos. 
    Los datos están segregados por clínica (RF-29).
    """
    # Garantiza que un psicólogo de la Clínica A no vea pacientes de la Clínica B.
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
# MÓDULO: GESTIÓN DE CITAS (NUEVO)
# TRAZABILIDAD: T005 (Diseño de BD Inicial) | SPRINT 0 (Completitud)
# ==============================================================================
class Cita(models.Model):
    """
    Entidad para la programación de sesiones. 
    Completa el esquema relacional básico solicitado en el Sprint 0.
    """
    # Relación uno a muchos: Un paciente puede tener múltiples citas.
    paciente = models.ForeignKey(
        Paciente,
        on_delete=models.CASCADE,
        related_name='citas'
    )

    # Restricción de integridad: Solo usuarios con rol PSICOLOGO pueden atender citas.
    psicologo = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'PSICOLOGO'},
        related_name='citas_asignadas'
    )

    fecha_hora = models.DateTimeField(help_text="RNF-05: Precisión temporal en citas")
    motivo = models.TextField(blank=True, null=True)

    # Estados de flujo para trazabilidad de la consulta.
    ESTADOS = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    estado = models.CharField(max_length=20, choices=ESTADOS, default='PENDIENTE')

    objects = models.Manager()

    class Meta:
        """Metadatos de la clase Cita."""
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        # Mejora: Ordenar por fecha por defecto
        ordering = ['fecha_hora']

    def __str__(self):
        return f"Cita: {self.paciente} con {self.psicologo} - {self.fecha_hora}"