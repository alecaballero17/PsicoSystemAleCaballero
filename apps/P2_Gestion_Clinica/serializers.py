from rest_framework import serializers
from .models import Paciente, ExpedienteClinico, NotaClinica, ArchivoAdjunto, Evolucion, DiagnosticoPaciente

class PacienteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paciente
        fields = [
            "id",
            "nombre",
            "ci",
            "fecha_nacimiento",
            "telefono",
            "motivo_consulta",
        ]

class NotaClinicaSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')

    class Meta:
        model = NotaClinica
        fields = ['id', 'psicologo', 'psicologo_nombre', 'contenido', 'fecha']

class ArchivoAdjuntoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ArchivoAdjunto
        fields = ['id', 'archivo', 'descripcion', 'fecha_subida']

class ExpedienteClinicoSerializer(serializers.ModelSerializer):
    notas = NotaClinicaSerializer(many=True, read_only=True)
    archivos = ArchivoAdjuntoSerializer(many=True, read_only=True)
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')

    class Meta:
        model = ExpedienteClinico
        fields = ['id', 'paciente', 'paciente_nombre', 'fecha_creacion', 'ultima_actualizacion', 'notas', 'archivos']

# ==============================================================================
# SPRINT 4: Serializers de Evolución y Diagnóstico (CU29)
# ==============================================================================
class EvolucionSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')
    estado_animo_display = serializers.ReadOnlyField(source='get_estado_animo_display')

    class Meta:
        model = Evolucion
        fields = [
            'id', 'paciente', 'psicologo', 'psicologo_nombre',
            'cita', 'fecha_sesion', 'diagnostico', 'observaciones',
            'estado_animo', 'estado_animo_display',
            'recomendacion', 'fecha_creacion'
        ]
        read_only_fields = ['psicologo']

class DiagnosticoPacienteSerializer(serializers.ModelSerializer):
    psicologo_nombre = serializers.ReadOnlyField(source='psicologo.get_full_name')
    estado_display = serializers.ReadOnlyField(source='get_estado_display')

    class Meta:
        model = DiagnosticoPaciente
        fields = [
            'id', 'paciente', 'psicologo', 'psicologo_nombre',
            'diagnostico_inicial', 'fecha_inicio',
            'diagnostico_final', 'fecha_fin',
            'estado', 'estado_display', 'fecha_creacion'
        ]
        read_only_fields = ['psicologo']

class PacienteDetalleSerializer(serializers.ModelSerializer):
    expediente = ExpedienteClinicoSerializer(read_only=True)
    diagnostico_global = DiagnosticoPacienteSerializer(read_only=True)
    evoluciones = EvolucionSerializer(many=True, read_only=True)

    class Meta:
        model = Paciente
        fields = '__all__'


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
            first_name=nombre,
            last_name=ci
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
