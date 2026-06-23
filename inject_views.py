import sys

view_code = """
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import PacienteRegistroPublicoSerializer
import logging

logger = logging.getLogger(__name__)

class PacienteRegistroPublicoAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PacienteRegistroPublicoSerializer(data=request.data)
        if serializer.is_valid():
            result = serializer.save()
            logger.info("NUEVO PACIENTE AUTO-REGISTRADO: %s", result["email"])
            return Response(
                {"message": "Registro completado con éxito.", "data": result},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class AssociateClinicAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        clinica_id = request.data.get('clinica_id')
        if not clinica_id:
            return Response({"detail": "Se requiere clinica_id."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            clinica = Clinica.objects.get(id=clinica_id)
            user = request.user
            
            user.clinica = clinica
            user.save()

            try:
                paciente = Paciente.objects.get(ci=user.username)
            except Paciente.DoesNotExist:
                paciente = Paciente.objects.filter(ci=user.username).first()

            if paciente:
                paciente.clinica = clinica
                paciente.save()

            return Response({
                "message": f"Vínculo exitoso con {clinica.nombre}",
                "clinica_id": clinica.id,
                "clinica_nombre": clinica.nombre
            }, status=status.HTTP_200_OK)

        except Clinica.DoesNotExist:
            return Response({"detail": "La clínica no existe."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)
"""

with open('apps/P2_Gestion_Clinica/views.py', 'a', encoding='utf-8') as f:
    f.write("\n" + view_code)
print("Added views to P2")
