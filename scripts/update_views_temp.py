import os

file_path = r'c:\Users\ElCremosasWee\PsicoSystem_SI2\apps\P4_IA_Administracion\views.py'

new_view = '''
from django.db.models import Count
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import openpyxl
from io import BytesIO
import base64
from apps.P1_Identidad_Acceso.models import Usuario

class VoiceToReportAPIView(APIView):
    """
    Endpoint híbrido que recibe texto de voz, extrae filtros con IA (Gemini) 
    y genera un reporte en PDF.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def post(self, request):
        transcript = request.data.get('transcript', '')
        if not transcript:
            return Response({"error": "No se recibió texto de voz."}, status=status.HTTP_400_BAD_REQUEST)

        clinica = request.user.clinica

        # 1. IA extrae filtros
        filtros = AIService.interpretar_comando_voz(transcript)
        if "error" in filtros:
            return Response(filtros, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # 2. Aplicar filtros ORM
        citas_query = Cita.objects.filter(paciente__clinica=clinica)
        transacciones_query = Transaccion.objects.filter(paciente__clinica=clinica)

        if filtros.get('fecha_inicio'):
            citas_query = citas_query.filter(fecha_hora__date__gte=filtros['fecha_inicio'])
            transacciones_query = transacciones_query.filter(fecha__date__gte=filtros['fecha_inicio'])
        
        if filtros.get('fecha_fin'):
            citas_query = citas_query.filter(fecha_hora__date__lte=filtros['fecha_fin'])
            transacciones_query = transacciones_query.filter(fecha__date__lte=filtros['fecha_fin'])

        if filtros.get('estado_cita'):
            citas_query = citas_query.filter(estado=filtros['estado_cita'].upper())

        if filtros.get('monto_min'):
            transacciones_query = transacciones_query.filter(monto__gte=filtros['monto_min'])
        
        if filtros.get('monto_max'):
            transacciones_query = transacciones_query.filter(monto__lte=filtros['monto_max'])

        psicologo_top = None
        if filtros.get('top_psicologo'):
            top = citas_query.values('psicologo').annotate(total=Count('id')).order_by('-total').first()
            if top:
                user = Usuario.objects.filter(id=top['psicologo']).first()
                if user:
                    psicologo_top = f"{user.get_full_name() or user.username} ({top['total']} citas)"

        # 3. Generar PDF
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()
        
        elements.append(Paragraph(f"Reporte Generado por IA - PsicoSystem", styles['Title']))
        elements.append(Paragraph(f"Clínica: {clinica.nombre}", styles['Normal']))
        elements.append(Spacer(1, 12))
        
        filtro_str = f"Filtros aplicados: {filtros}"
        elements.append(Paragraph(filtro_str, styles['Normal']))
        elements.append(Spacer(1, 12))

        if psicologo_top:
            elements.append(Paragraph(f"Psicólogo Destacado: {psicologo_top}", styles['Heading2']))
            elements.append(Spacer(1, 12))

        # Tabla de Citas
        data = [["Paciente", "Psicólogo", "Fecha", "Estado"]]
        for c in citas_query[:50]: # Limitar a 50 para el pdf demo
            data.append([
                c.paciente.nombre[:20], 
                c.psicologo.username, 
                c.fecha_hora.strftime("%Y-%m-%d %H:%M"), 
                c.estado
            ])
        
        if len(data) > 1:
            table = Table(data)
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(table)
        else:
            elements.append(Paragraph("No se encontraron citas con estos filtros.", styles['Normal']))

        doc.build(elements)
        
        pdf_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        buffer.close()

        # Auditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Generó un reporte por IA. Filtros: {filtros}"
        )

        return Response({
            "filtros": filtros,
            "pdf_base64": pdf_base64
        }, status=status.HTTP_200_OK)
'''

with open(file_path, 'a', encoding='utf-8') as f:
    f.write('\n' + new_view)
print('Done appending VoiceToReportAPIView.')
