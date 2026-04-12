"""
[SPRINT 1 - T011] Serializer JWT personalizado con inyección de metadatos.
Extiende TokenObtainPairSerializer para incluir rol y clínica en la respuesta.
"""

from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """[SPRINT 1 - T011] [RF-01] [RF-28] [RF-29] Inyecta rol y clínica en la respuesta JWT."""

    # pylint: disable=abstract-method

    def validate(self, attrs):
        data = super().validate(attrs)

        data["role"] = self.user.rol
        data["username"] = self.user.username

        if self.user.clinica:
            data["clinica_id"] = self.user.clinica.id
            data["clinica_nombre"] = self.user.clinica.nombre
        else:
            data["clinica_id"] = None
            data["clinica_nombre"] = "Administrador Global"

        return data
