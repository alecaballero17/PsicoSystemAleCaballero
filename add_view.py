import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add the import if not present
if 'from apps.P1_Identidad_Acceso.models import DispositivoMovil' not in content:
    content = content.replace(
        'from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador, RequiresModuloContabilidad, RequiresModuloIA\nfrom apps.P2_Gestion_Clinica.models import Paciente, EvolucionClinica',
        'from apps.P1_Identidad_Acceso.models import DispositivoMovil\nfrom apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador, RequiresModuloContabilidad, RequiresModuloIA\nfrom apps.P2_Gestion_Clinica.models import Paciente, EvolucionClinica'
    )

new_view = '''
class RegistroTokenFCMAPIView(APIView):
    """
    Registra el token de dispositivo (Firebase Cloud Messaging) para enviar notificaciones Push.
    """
    permission_classes = [IsAuthenticated, EsPaciente]

    def post(self, request):
        fcm_token = request.data.get('fcm_token')

        if not fcm_token:
            return Response({"error": "Debe proveer fcm_token"}, status=status.HTTP_400_BAD_REQUEST)

        # Actualizar o crear el dispositivo para este usuario
        dispositivo, created = DispositivoMovil.objects.update_or_create(
            usuario=request.user,
            defaults={'fcm_token': fcm_token}
        )

        return Response({
            "mensaje": "Token registrado exitosamente para notificaciones Push.",
            "fcm_token": dispositivo.fcm_token
        }, status=status.HTTP_200_OK)
'''

if 'class RegistroTokenFCMAPIView' not in content:
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content + '\n' + new_view)
    print("Added view")
else:
    print("View already exists")
