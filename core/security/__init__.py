from .permissions import IsPsicologo, IsAdmin
from .auth_views import CustomTokenObtainPairView, LogoutAPIView, MeAPIView
from .jwt_serializers import CustomTokenObtainPairSerializer  # <-- AGREGA ESTA LÍNEA
