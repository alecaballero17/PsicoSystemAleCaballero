from rest_framework import serializers

from .models import Cita


class CitaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cita
        fields = ["id", "paciente", "psicologo", "fecha_hora", "motivo", "estado"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not user.clinica_id:
            raise serializers.ValidationError("Sesión o clínica no válida.")

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

        return attrs
