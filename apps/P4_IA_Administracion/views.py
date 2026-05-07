from decimal import Decimal
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

import requests
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
