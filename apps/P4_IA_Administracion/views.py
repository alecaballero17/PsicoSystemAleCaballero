import io
import base64
import datetime
import uuid
import os

from decimal import Decimal
from django.db.models import Sum, Count, Max
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import requests
from apps.P1_Identidad_Acceso.models import DispositivoMovil, Usuario
from apps.P1_Identidad_Acceso.permissions import HasClinicaAsignada, EsAdministrador, EsPsicologoOAdministrador, RequiresModuloContabilidad, RequiresModuloIA
from apps.P2_Gestion_Clinica.models import Paciente, EvolucionClinica
from apps.P3_Logistica_Citas.models import Cita
from .models import LogAuditoria, Transaccion, Comprobante
from .serializers import TransaccionSerializer, ComprobanteSerializer
from .services.ai_service import AIService

class LogAuditoriaAPIView(APIView):
    """
    Endpoint de bitácora exclusivo para el Administrador de la clínica.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def get(self, request):
        clinica = request.user.clinica
        logs = LogAuditoria.objects.filter(usuario__clinica=clinica).order_by('-fecha')[:50]
        
        data = [
            {
                "fecha": log.fecha.strftime("%Y-%m-%d %H:%M:%S"),
                "usuario": getattr(log.usuario, "username", "Desconocido") if log.usuario else "Desconocido",
                "accion": log.accion
            }
            for log in logs
        ]
        return Response(data, status=status.HTTP_200_OK)

class DashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, HasClinicaAsignada]

    def get(self, request):
        clinica = request.user.clinica
        total_pacientes = Paciente.objects.filter(clinica=clinica).count() if clinica else 0
        citas_pendientes = Cita.objects.filter(
            paciente__clinica=clinica, estado="PENDIENTE"
        ).count() if clinica else 0

        data = {
            "clinica": clinica.nombre if clinica else "Sin Clínica",
            "metricas": {
                "total_pacientes": total_pacientes,
                "citas_pendientes": citas_pendientes,
            },
        }
        return Response(data, status=status.HTTP_200_OK)

# --- Módulo Financiero ---

class TransaccionViewSet(viewsets.ModelViewSet):
    serializer_class = TransaccionSerializer
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloContabilidad]

    def get_queryset(self):
        return Transaccion.objects.filter(paciente__clinica=self.request.user.clinica)

    def perform_create(self, serializer):
        transaccion = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Registró transacción ({transaccion.tipo}) de {transaccion.monto} para {transaccion.paciente.nombre}"
        )

class SaldoPacienteView(APIView):
    """
    Calcula el saldo actual (deuda) de un paciente.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloContabilidad]

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente, id=paciente_id, clinica=request.user.clinica)
        
        pagos = Transaccion.objects.filter(paciente=paciente, tipo='PAGO').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        deudas = Transaccion.objects.filter(paciente=paciente, tipo='DEUDA').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        ajustes = Transaccion.objects.filter(paciente=paciente, tipo='AJUSTE').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        saldo = deudas - pagos + ajustes
        
        return Response({
            "paciente": paciente.nombre,
            "total_pagado": pagos,
            "total_deuda_acumulada": deudas,
            "saldo_pendiente": saldo
        }, status=status.HTTP_200_OK)

class GenerarComprobantePDFView(APIView):
    """
    Genera un PDF de comprobante para una transacción de pago.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloContabilidad]

    def get(self, request, transaccion_id):
        transaccion = get_object_or_404(
            Transaccion, 
            id=transaccion_id, 
            paciente__clinica=request.user.clinica,
            tipo='PAGO'
        )
        
        # Lógica simplificada de PDF usando reportlab
        from reportlab.pdfgen import canvas
        import io

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer)
        
        p.drawString(100, 800, f"PsicoSystem - Comprobante de Pago")
        p.drawString(100, 780, f"Clínica: {request.user.clinica.nombre}")
        p.drawString(100, 750, f"Paciente: {transaccion.paciente.nombre}")
        p.drawString(100, 730, f"Fecha: {transaccion.fecha.strftime('%Y-%m-%d %H:%M')}")
        p.drawString(100, 710, f"Monto: {transaccion.monto} BOB")
        p.drawString(100, 690, f"Descripción: {transaccion.descripcion}")
        
        p.showPage()
        p.save()
        
        buffer.seek(0)
        return HttpResponse(buffer, content_type='application/pdf')

# --- IA Diagnostics ---

class AnalisisIAView(APIView):
    """
    Endpoint para disparar el análisis de IA llamando al Microservicio FastAPI.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsPsicologoOAdministrador, RequiresModuloIA]

    def post(self, request, evolucion_id):
        evolucion = get_object_or_404(
            EvolucionClinica, 
            id=evolucion_id, 
            historia__paciente__clinica=request.user.clinica
        )
        
        if not evolucion.notas_sesion:
            return Response(
                {"error": "La nota de sesión está vacía."}, 
                status=status.HTTP_400_BAD_REQUEST
            )

        # Llamada al Microservicio Externo
        try:
            response = requests.post(
                "http://127.0.0.1:8001/api/v1/analyze",
                json={"notas": evolucion.notas_sesion},
                timeout=5
            )
            response.raise_for_status()
            resultado = response.json()
            evolucion.analisis_ia = str(resultado)
            evolucion.save()
        except Exception as e:
            return Response(
                {"error": f"Error del Microservicio de IA: {str(e)}"}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Ejecutó análisis de IA (Vía Microservicio) para la sesión de: {evolucion.historia.paciente.nombre}"
        )

        return Response({"analisis_ia": resultado}, status=status.HTTP_200_OK)


import os
import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from gtts import gTTS

class ReportePersonalizadoAPIView(APIView):
    """
    Genera un reporte personalizado por rango de fechas y opcionalmente un archivo de audio (MP3).
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def post(self, request):
        fecha_inicio = request.data.get('fecha_inicio')
        fecha_fin = request.data.get('fecha_fin')
        generar_audio = request.data.get('generar_audio', True)

        if not fecha_inicio or not fecha_fin:
            return Response({"error": "Debe proveer fecha_inicio y fecha_fin (YYYY-MM-DD)"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            inicio = datetime.datetime.strptime(fecha_inicio, '%Y-%m-%d')
            fin = datetime.datetime.strptime(fecha_fin, '%Y-%m-%d')
            # Ajustar el fin de día para incluir todo el día
            fin = fin.replace(hour=23, minute=59, second=59)
        except ValueError:
            return Response({"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, status=status.HTTP_400_BAD_REQUEST)

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
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "texto": texto_reporte,
            "audio_url": audio_url
        }, status=status.HTTP_200_OK)


from apps.P1_Identidad_Acceso.permissions import EsPaciente

class MobileSaldoPacienteView(APIView):
    """
    Endpoint para que la app móvil (Flutter) consulte la deuda del paciente.
    """
    permission_classes = [IsAuthenticated, EsPaciente]

    def get(self, request, paciente_id):
        paciente = get_object_or_404(Paciente, id=paciente_id)
        
        pagos = Transaccion.objects.filter(paciente=paciente, tipo='PAGO').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        deudas = Transaccion.objects.filter(paciente=paciente, tipo='DEUDA').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')
        ajustes = Transaccion.objects.filter(paciente=paciente, tipo='AJUSTE').aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        saldo = deudas - pagos + ajustes
        
        return Response({
            "paciente_id": paciente.id,
            "paciente_nombre": paciente.nombre,
            "total_pagado": pagos,
            "total_deuda_acumulada": deudas,
            "saldo_pendiente": saldo
        }, status=status.HTTP_200_OK)

class PasarelaPagoMobileAPIView(APIView):
    """
    Endpoint que simula la pasarela de pagos para la aplicación Flutter.
    """
    permission_classes = [IsAuthenticated, EsPaciente]

    def post(self, request):
        paciente_id = request.data.get('paciente_id')
        monto = request.data.get('monto')
        metodo_pago = request.data.get('metodo_pago', 'TARJETA')
        numero_tarjeta = request.data.get('numero_tarjeta', '')

        if not paciente_id or not monto:
            return Response({"error": "Debe proveer paciente_id y monto."}, status=status.HTTP_400_BAD_REQUEST)

        # Validación MUY básica para facilitar las pruebas del Frontend
        # En la vida real, aquí se llamaría a la API de Stripe o PayPal.
        if len(str(numero_tarjeta)) < 4:
            return Response({"error": "La tarjeta debe tener al menos 4 números para ser procesada."}, status=status.HTTP_400_BAD_REQUEST)

        paciente = get_object_or_404(Paciente, id=paciente_id)

        try:
            monto_decimal = Decimal(str(monto))
        except:
            return Response({"error": "Monto inválido."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Registrar la transacción de Pago
        transaccion = Transaccion.objects.create(
            paciente=paciente,
            monto=monto_decimal,
            tipo='PAGO',
            descripcion=f"Pago Móvil via {metodo_pago} (****{numero_tarjeta[-4:]})"
        )

        # 2. Generar el Comprobante automáticamente
        nro_comp = f"MOB-{uuid.uuid4().hex[:8].upper()}"
        comprobante = Comprobante.objects.create(
            transaccion=transaccion,
            nro_comprobante=nro_comp
        )

        # 3. Auditoria
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"Pago móvil registrado ({monto_decimal} BOB) para el paciente {paciente.nombre}"
        )

        # 4. Enviar Notificación Push (Simulada para la Defensa)
        dispositivos = DispositivoMovil.objects.filter(usuario=request.user)
        for dispositivo in dispositivos:
            # Aquí iría la lógica real de firebase-admin. Ej: messaging.send(...)
            print(f"\n[FIREBASE PUSH SIMULATOR] Enviando notificación de Pago Exitoso al token: {dispositivo.fcm_token}")
            print(f"[FIREBASE PUSH SIMULATOR] Titulo: Pago Aprobado")
            print(f"[FIREBASE PUSH SIMULATOR] Cuerpo: Su pago de {monto_decimal} BOB ha sido procesado con éxito.\n")

        return Response({
            "mensaje": "Pago procesado exitosamente por la pasarela virtual.",
            "transaccion_id": transaccion.id,
            "comprobante": nro_comp,
            "monto_pagado": monto_decimal
        }, status=status.HTTP_201_CREATED)


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


# ==============================================================================
# NUEVO: LISTADO DE CITAS CON FILTROS MANUALES (Tabla del reporte)
# ==============================================================================
class CitasReporteListAPIView(APIView):
    """
    Devuelve la lista de citas de la clínica con filtros opcionales:
    - fecha_inicio / fecha_fin
    - estado (PENDIENTE, COMPLETADA, CANCELADA, NO_ASISTIO)
    Solo accesible por ADMIN.
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def get(self, request):
        clinica = request.user.clinica
        qs = Cita.objects.filter(paciente__clinica=clinica).select_related('paciente', 'psicologo')

        fecha_inicio = request.query_params.get('fecha_inicio')
        fecha_fin = request.query_params.get('fecha_fin')
        estado = request.query_params.get('estado')

        if fecha_inicio:
            try:
                qs = qs.filter(fecha_hora__date__gte=datetime.date.fromisoformat(fecha_inicio))
            except ValueError:
                pass
        if fecha_fin:
            try:
                qs = qs.filter(fecha_hora__date__lte=datetime.date.fromisoformat(fecha_fin))
            except ValueError:
                pass
        if estado and estado in ['PENDIENTE', 'COMPLETADA', 'CANCELADA', 'NO_ASISTIO']:
            qs = qs.filter(estado=estado)

        data = [
            {
                "id": c.id,
                "paciente": c.paciente.nombre,
                "psicologo": c.psicologo.get_full_name() or c.psicologo.username,
                "fecha_hora": c.fecha_hora.strftime("%Y-%m-%d %H:%M"),
                "estado": c.estado,
                "motivo": c.motivo or "",
            }
            for c in qs.order_by('-fecha_hora')[:200]
        ]
        return Response({"total": len(data), "citas": data}, status=status.HTTP_200_OK)


# ==============================================================================
# NUEVO: VOICE-TO-REPORT CON IA (RF-27 Extendido)
# ==============================================================================
class VoiceToReportAPIView(APIView):
    """
    Recibe el texto transcrito de la voz del administrador,
    usa Gemini para extraer filtros, aplica las queries al ORM de Django
    y genera un reporte PDF + Excel.

    POST /api/reportes/voz/
    Body: { "transcript": "citas canceladas de enero a marzo" }
    Returns: { "filtros": {...}, "pdf_base64": "...", "resumen": {...} }
    """
    permission_classes = [IsAuthenticated, HasClinicaAsignada, EsAdministrador]

    def post(self, request):
        transcript = request.data.get('transcript', '').strip()
        if not transcript:
            return Response({"error": "Debe proveer el campo 'transcript' con el texto dictado."}, status=status.HTTP_400_BAD_REQUEST)

        # 1. Interpretar el comando con Gemini
        filtros = AIService.interpretar_comando_voz(transcript)
        if 'error' in filtros:
            return Response({"error": filtros['error']}, status=status.HTTP_502_BAD_GATEWAY)

        clinica = request.user.clinica

        # 2. Aplicar filtros a la tabla de Citas
        qs_citas = Cita.objects.filter(paciente__clinica=clinica).select_related('paciente', 'psicologo')

        if filtros.get('fecha_inicio'):
            try:
                qs_citas = qs_citas.filter(fecha_hora__date__gte=datetime.date.fromisoformat(filtros['fecha_inicio']))
            except (ValueError, TypeError):
                pass
        if filtros.get('fecha_fin'):
            try:
                qs_citas = qs_citas.filter(fecha_hora__date__lte=datetime.date.fromisoformat(filtros['fecha_fin']))
            except (ValueError, TypeError):
                pass
        if filtros.get('estado_cita'):
            qs_citas = qs_citas.filter(estado=filtros['estado_cita'])

        citas = list(qs_citas.order_by('-fecha_hora')[:500])
        total_citas = len(citas)

        # 3. Psicólogo con más citas (si se pidió)
        top_psicologo_info = None
        if filtros.get('top_psicologo'):
            top = qs_citas.values('psicologo__username', 'psicologo__first_name', 'psicologo__last_name') \
                          .annotate(total=Count('id')).order_by('-total').first()
            if top:
                nombre = f"{top.get('psicologo__first_name','')} {top.get('psicologo__last_name','')}".strip()
                top_psicologo_info = {
                    "nombre": nombre or top.get('psicologo__username', 'N/A'),
                    "total_citas": top['total']
                }

        # 4. Filtros de monto en Transacciones
        qs_trans = Transaccion.objects.filter(paciente__clinica=clinica, tipo='PAGO')
        if filtros.get('monto_min') is not None:
            try:
                qs_trans = qs_trans.filter(monto__gte=Decimal(str(filtros['monto_min'])))
            except Exception:
                pass
        if filtros.get('monto_max') is not None:
            try:
                qs_trans = qs_trans.filter(monto__lte=Decimal(str(filtros['monto_max'])))
            except Exception:
                pass
        total_recaudado = qs_trans.aggregate(total=Sum('monto'))['total'] or Decimal('0.00')

        # 5. Generar PDF con ReportLab
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                                topMargin=2*cm, bottomMargin=2*cm)
        styles = getSampleStyleSheet()
        elements = []

        # Encabezado
        elements.append(Paragraph(f"<b>PsicoSystem — Reporte por Voz IA</b>", styles['Title']))
        elements.append(Paragraph(f"Clínica: {clinica.nombre}", styles['Normal']))
        elements.append(Paragraph(f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", styles['Normal']))
        elements.append(Paragraph(f"Comando dictado: \"{transcript}\"", styles['Italic']))
        elements.append(Spacer(1, 0.5*cm))

        # Resumen
        filtros_txt = []
        if filtros.get('fecha_inicio'): filtros_txt.append(f"Desde: {filtros['fecha_inicio']}")
        if filtros.get('fecha_fin'): filtros_txt.append(f"Hasta: {filtros['fecha_fin']}")
        if filtros.get('estado_cita'): filtros_txt.append(f"Estado: {filtros['estado_cita']}")
        if filtros.get('monto_min'): filtros_txt.append(f"Monto mín: {filtros['monto_min']} BOB")
        if filtros.get('monto_max'): filtros_txt.append(f"Monto máx: {filtros['monto_max']} BOB")

        elements.append(Paragraph(f"<b>Filtros aplicados:</b> {' | '.join(filtros_txt) or 'Ninguno'}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total de citas encontradas:</b> {total_citas}", styles['Normal']))
        elements.append(Paragraph(f"<b>Total recaudado (pagos filtrados):</b> {total_recaudado} BOB", styles['Normal']))
        if top_psicologo_info:
            elements.append(Paragraph(f"<b>Psicólogo más activo:</b> {top_psicologo_info['nombre']} ({top_psicologo_info['total_citas']} citas)", styles['Normal']))
        elements.append(Spacer(1, 0.5*cm))

        # Tabla de citas
        if citas:
            table_data = [["#", "Paciente", "Psicólogo", "Fecha/Hora", "Estado", "Motivo"]]
            for i, c in enumerate(citas[:100], 1):  # Limitar a 100 filas en PDF
                table_data.append([
                    str(i),
                    c.paciente.nombre[:25],
                    (c.psicologo.get_full_name() or c.psicologo.username)[:20],
                    c.fecha_hora.strftime("%d/%m/%Y %H:%M"),
                    c.estado,
                    (c.motivo or "")[:30],
                ])
            t = Table(table_data, repeatRows=1)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2563eb')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')]),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            elements.append(t)

        doc.build(elements)
        buffer.seek(0)
        pdf_base64 = base64.b64encode(buffer.read()).decode('utf-8')

        # 6. Auditoría
        LogAuditoria.objects.create(
            usuario=request.user,
            accion=f"[VOICE-IA] Reporte por voz generado. Transcript: '{transcript[:80]}'. Citas: {total_citas}."
        )

        return Response({
            "filtros_interpretados": filtros,
            "resumen": {
                "total_citas": total_citas,
                "total_recaudado_bobs": str(total_recaudado),
                "top_psicologo": top_psicologo_info,
            },
            "pdf_base64": pdf_base64,
        }, status=status.HTTP_200_OK)
