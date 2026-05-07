import os
import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\views.py'

new_view = '''
import os
import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from gtts import gTTS

class ReportePersonalizadoAPIView(APIView):
    \"\"\"
    Genera un reporte personalizado por rango de fechas y opcionalmente un archivo de audio (MP3).
    \"\"\"
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def post(self, request):
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        generar_audio = request.data.get('generar_audio', True)

        if not fecha_inicio or not fecha_fin:
            return Response({\"error\": \"Debe proveer fecha_inicio y fecha_fin (YYYY-MM-DD)\"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Ajustar el fin de día para incluir todo el día
            fin = fin.replace(hour=23, minute=59, second=59)
        except ValueError:
            return Response({\"error\": \"Formato de fecha inválido. Use YYYY-MM-DD\"}, status=status.HTTP_400_BAD_REQUEST)

        clinica = request.user.clinica

        # Consultas
        pacientes_nuevos = Paciente.objects.filter(clinica=clinica, fecha_registro__range=(inicio, fin)).count()
        
        pagos = Transaccion.objects.filter(
            paciente__clinica=clinica, 
            fecha__range=(inicio, fin), 
            tipo='PAGO'
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        
        deudas = Transaccion.objects.filter(
            paciente__clinica=clinica, 
            fecha__range=(inicio, fin), 
            tipo='DEUDA'
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # Generar Texto del Reporte
        texto_reporte = (
            f"Reporte ejecutivo de la clínica {clinica.nombre}. "
            f"Desde el {inicio.strftime('%d de %B de %Y')} hasta el {fin.strftime('%d de %B de %Y')}. "
            f"Durante este período se registraron {pacientes_nuevos} pacientes nuevos. "
            f"El total de ingresos por pagos de sesiones fue de {pagos} bolivianos. "
            f"Y el total de deuda acumulada o cargos pendientes fue de {deudas} bolivianos. "
            f"Fin del reporte."
        )

        audio_url = None
        if generar_audio:
            try:
                # Usar gTTS para generar el audio en español
                tts = gTTS(text=texto_reporte, lang='es', tld='com.mx')
                
                # Crear directorio si no existe
                reportes_dir = os.path.join(settings.MEDIA_ROOT, 'reportes_audio')
                if not os.path.exists(reportes_dir):
                    os.makedirs(reportes_dir)
                    
                timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
                filename = f"reporte_{clinica.id}_{timestamp}.mp3"
                filepath = os.path.join(reportes_dir, filename)
                
                tts.save(filepath)
                audio_url = settings.MEDIA_URL + f"reportes_audio/{filename}"
            except Exception as e:
                # Si falla el audio, retornamos el texto igual
                print(f"Error generando audio TTS: {e}")

        # Auditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Generó un reporte personalizado del {fecha_inicio} al {fecha_fin} (Audio: {generar_audio})"
        )

        return Response({
            \"fecha_inicio\": fecha_inicio,
            \"fecha_fin\": fecha_fin,
            \"texto\": texto_reporte,
            \"audio_url\": audio_url
        }, status=status.HTTP_200_OK)
'''

with open(file_path, 'a', encoding='utf-8') as f:
    f.write('\n' + new_view)
print('Done appending view.')
