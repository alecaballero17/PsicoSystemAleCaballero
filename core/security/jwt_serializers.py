from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Trazabilidad: RF-01 (JWT), RF-28 (Roles), RF-29 (Multi-tenant)
    Inyecta metadatos del usuario en la respuesta del Login para optimizar el Frontend.
    """

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
