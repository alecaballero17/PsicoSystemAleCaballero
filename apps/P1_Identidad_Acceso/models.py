from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractUser

# ==============================================================================
# MÓDULO: GESTIÓN ORGANIZACIONAL (TENANT)
# ==============================================================================
class Clinica(models.Model):
    nombre = models.CharField(max_length=100)
    nit = models.CharField(max_length=20, unique=True)
    direccion = models.TextField()
    telefono = models.CharField(max_length=20, blank=True, default='')
    email_contacto = models.EmailField(blank=True, default='')
    logo = models.ImageField(upload_to='logos/', blank=True, null=True)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    
    # Nuevos campos solicitados para la app móvil
    especialidades = models.TextField(blank=True, default='', help_text="Lista de especialidades de la clínica, separadas por comas")
    horarios_atencion = models.CharField(max_length=255, blank=True, default='Lunes a Viernes 08:00 - 18:00')

    PLANES = [
        ('Basico', 'Básico'),
        ('Profesional', 'Profesional'),
        ('Premium', 'Premium'),
    ]
    plan_suscripcion = models.CharField(max_length=50, choices=PLANES, default='Basico')

    def __str__(self):
        return str(self.nombre)

class TransaccionClinica(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.CASCADE, related_name='transacciones_facturacion')
    tipo = models.CharField(max_length=50, choices=[
        ('CARGA', 'Carga de Saldo'), 
        ('PAGO_SUSCRIPCION', 'Pago de Suscripción'), 
        ('INGRESO_PACIENTE', 'Ingreso por Pago de Paciente'),
        ('OTRO', 'Otro')
    ])
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    descripcion = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=50, default='TRANSFERENCIA')

    def __str__(self):
        return f"{self.clinica.nombre} - {self.tipo} - {self.monto}"

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
    ci = models.CharField(max_length=20, blank=True, default='')
    
    # Control de Cancelaciones (Reglas de Negocio)
    cancelaciones_hoy = models.IntegerField(default=0)
    ultima_cancelacion_fecha = models.DateField(null=True, blank=True)
    
    # Seguridad: Cambio de contraseña cada 90 días
    ultimo_cambio_password = models.DateTimeField(default=timezone.now)
    debe_cambiar_password = models.BooleanField(default=False)

    # Campos legacy/huérfanos en la base de datos (se mantienen para evitar IntegrityError)
    forzar_cambio_pass = models.BooleanField(default=False)
    ultima_fecha_pass = models.DateTimeField(default=timezone.now)
    horario_atencion = models.CharField(max_length=200, blank=True, default='')
    email_notif_citas = models.BooleanField(default=True)
    email_notif_reportes = models.BooleanField(default=True)
    push_notif_alertas = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        # Si es un usuario nuevo o si la contraseña está siendo actualizada
        is_new = self.pk is None
        password_changed = False
        
        if not is_new:
            try:
                old_user = Usuario.objects.get(pk=self.pk)
                if self.password != old_user.password:
                    password_changed = True
            except Usuario.DoesNotExist:
                is_new = True
        
        if is_new or password_changed:
            self.ultimo_cambio_password = timezone.now()
            self.debe_cambiar_password = False
            
        super().save(*args, **kwargs)


# ==============================================================================
# MÓDULO: NOTIFICACIONES PUSH (MÓVIL)
# ==============================================================================
class DispositivoMovil(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='dispositivos')
    fcm_token = models.CharField(max_length=255, unique=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Dispositivo de {self.usuario.username}"

class NotificacionPush(models.Model):
    usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='notificaciones')
    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    leido = models.BooleanField(default=False)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha_creacion']

    def __str__(self):
        return f"Notificacion para {self.usuario.username} - {self.titulo}"
