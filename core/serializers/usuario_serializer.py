from rest_framework import serializers
from core.models import Usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """
    Trazabilidad: CU-01 | RF-01 (JWT) | RF-28 (Roles)
    Maneja la representación de usuarios con validación de integridad organizacional.
    """

    clinica_nombre = serializers.CharField(source="clinica.nombre", read_only=True)

    class Meta:
        model = Usuario
        fields = [
            "id",
            "username",
            "email",
            "password",
            "clinica",
            "clinica_nombre",
            "rol",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def validate_clinica(self, value):
        """
        RNF-08: Validación de datos de negocio.
        Garantiza que ningún usuario se cree sin una clínica raíz.
        """
        if not value:
            raise serializers.ValidationError(
                "Es obligatorio asignar una clínica para cumplir con el aislamiento de datos (RF-29)."
            )
        return value

    def create(self, validated_data):
        user = Usuario.objects.create_user(**validated_data)
        return user
