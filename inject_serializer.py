import sys

serializer_code = """
from apps.P1_Identidad_Acceso.models import Usuario, Clinica
from django.contrib.auth.hashers import make_password
from django.utils import timezone
try:
    from apps.P6_ReportesComunicaciones.models import NotificacionPush
except ImportError:
    pass

class PacienteRegistroPublicoSerializer(serializers.Serializer):
    clinica_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    nombre = serializers.CharField(max_length=100)
    ci = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    telefono = serializers.CharField(max_length=20, required=False, allow_blank=True)

    def validate_clinica_id(self, value):
        if value is None:
            return None
        try:
            return Clinica.objects.get(pk=value)
        except Clinica.DoesNotExist:
            raise serializers.ValidationError("La clínica seleccionada no existe.")

    def validate_email(self, value):
        if Usuario.objects.filter(email=value).exists() or Usuario.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este correo ya está registrado.")
        return value

    def validate_ci(self, value):
        if Paciente.objects.filter(ci=value).exists():
            raise serializers.ValidationError("Esta Cédula de Identidad ya está registrada.")
        return value

    def create(self, validated_data):
        clinica = validated_data.pop('clinica_id', None)
        nombre = validated_data['nombre']
        ci = validated_data['ci']
        email = validated_data['email']
        raw_password = validated_data['password']
        telefono = validated_data.get('telefono', '00000000')

        # Crear Usuario
        usuario = Usuario.objects.create(
            username=email,
            email=email,
            password=make_password(raw_password),
            rol='PACIENTE',
            clinica=clinica,
            ci=ci,
            first_name=nombre
        )

        # Crear Paciente
        paciente = Paciente.objects.create(
            nombre=nombre,
            ci=ci,
            clinica=clinica,
            fecha_nacimiento="1900-01-01",
            telefono=telefono,
            motivo_consulta="Registro Móvil"
        )
        
        try:
            hora_actual = timezone.localtime(timezone.now()).strftime("%H:%M")
            titulo_notif = "¡Bienvenido a PsicoSystem!"
            mensaje_notif = f"Hola {usuario.username}, tu cuenta ha sido creada exitosamente a las {hora_actual}. ¡Nos alegra tenerte aquí!"
            NotificacionPush.objects.create(
                usuario=usuario,
                titulo=titulo_notif,
                mensaje=mensaje_notif
            )
        except Exception:
            pass

        return {
            "nombre": paciente.nombre,
            "ci": paciente.ci,
            "email": usuario.email,
        }
"""

with open('apps/P2_Gestion_Clinica/serializers.py', 'a', encoding='utf-8') as f:
    f.write("\n" + serializer_code)
print("Added PacienteRegistroPublicoSerializer")
