from datetime import timedelta

from django.db.models import Q
from rest_framework import serializers

from .models import Cita, ListaEspera

# ==============================================================================
# T030: Duración estándar de sesión psicológica = 1 hora (50 min + 10 min buffer)
# ==============================================================================
DURACION_SESION = timedelta(hours=1)


class CitaSerializer(serializers.ModelSerializer):
    """
    Serializer de Cita con validación multi-tenant y detección de colisiones.
    RF-06 / RF-07 / T030.
    """
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    psicologo_nombre = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Cita
        fields = [
            "id", "paciente", "paciente_nombre",
            "psicologo", "psicologo_nombre",
            "fecha_hora", "motivo", "estado",
        ]

    def get_psicologo_nombre(self, obj):
        p = obj.psicologo
        nombre = f"{p.first_name} {p.last_name}".strip()
        return nombre if nombre else p.username

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not user.clinica_id:
            raise serializers.ValidationError("Sesión o clínica no válida.")

        # --- Validación de pertenencia al tenant ---
        paciente = attrs.get("paciente")
        if paciente is None and self.instance:
            paciente = self.instance.paciente
        if paciente and paciente.clinica_id != user.clinica_id:
            raise serializers.ValidationError(
                {"paciente": "El paciente no pertenece a tu clínica."}
            )

        psicologo = attrs.get("psicologo")
        if psicologo is None and self.instance:
            psicologo = self.instance.psicologo
        if psicologo:
            if psicologo.clinica_id != user.clinica_id:
                raise serializers.ValidationError(
                    {"psicologo": "El profesional no pertenece a tu clínica."}
                )
            if psicologo.rol != "PSICOLOGO":
                raise serializers.ValidationError(
                    {"psicologo": "Debe ser un usuario con rol psicólogo."}
                )

        # ==============================================================
        # T030: VALIDACIÓN DE COLISIONES DE HORARIO (bloques de 1 hora)
        # ==============================================================
        fecha_hora = attrs.get("fecha_hora")
        if fecha_hora and psicologo:
            inicio_bloque = fecha_hora
            fin_bloque = fecha_hora + DURACION_SESION

            colision_qs = Cita.objects.filter(
                psicologo=psicologo,
                fecha_hora__lt=fin_bloque,
                fecha_hora__gte=inicio_bloque - DURACION_SESION,
            ).exclude(estado="CANCELADA")

            # Excluir la cita actual en caso de actualización
            if self.instance:
                colision_qs = colision_qs.exclude(pk=self.instance.pk)

            if colision_qs.exists():
                raise serializers.ValidationError(
                    {"fecha_hora": "El psicólogo ya tiene una cita en ese horario."}
                )

            # Colisión del Paciente (No puede estar en 2 clínicas a la misma hora)
            colision_paciente_qs = Cita.objects.filter(
                paciente=paciente,
                fecha_hora__lt=fin_bloque,
                fecha_hora__gte=inicio_bloque - DURACION_SESION,
            ).exclude(estado="CANCELADA")

            if self.instance:
                colision_paciente_qs = colision_paciente_qs.exclude(pk=self.instance.pk)

            if colision_paciente_qs.exists():
                raise serializers.ValidationError(
                    {"fecha_hora": "Ya tienes una cita programada en este horario (posiblemente en otra clínica). No puedes estar en dos lugares a la vez."}
                )

        return attrs


class ListaEsperaSerializer(serializers.ModelSerializer):
    """T031: Serializer para la Lista de Espera con prioridad."""
    paciente_nombre = serializers.CharField(source='paciente.nombre', read_only=True)
    prioridad_display = serializers.SerializerMethodField(read_only=True)

    PRIORIDADES = {1: 'Alta', 2: 'Media', 3: 'Baja'}

    class Meta:
        model = ListaEspera
        fields = [
            "id", "paciente", "paciente_nombre",
            "prioridad", "prioridad_display",
            "observacion", "fecha_registro", "activo",
        ]
        read_only_fields = ["fecha_registro"]

    def get_prioridad_display(self, obj):
        return self.PRIORIDADES.get(obj.prioridad, 'Desconocida')
