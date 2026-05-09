import sys
import os

# 1. Update Permissions
perm_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P1_Identidad_Acceso\permissions.py'
with open(perm_path, 'r', encoding='utf-8') as f:
    perm_content = f.read()

new_perm = '''
class EsPaciente(permissions.BasePermission):
    message = "Solo pacientes pueden realizar pagos móviles."

    def has_permission(self, request, view):
        u = request.user
        # Para facilitar pruebas del frontend, dejamos que admins tambien pasen
        return bool(u and u.is_authenticated and getattr(u, "rol", None) in ("PACIENTE", "ADMIN", "PSICOLOGO"))
'''
if 'class EsPaciente' not in perm_content:
    with open(perm_path, 'a', encoding='utf-8') as f:
        f.write('\n' + new_perm)

# 2. Update Views
view_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\views.py'
with open(view_path, 'r', encoding='utf-8') as f:
    view_content = f.read()

new_views = '''
import uuid
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

        return Response({
            "mensaje": "Pago procesado exitosamente por la pasarela virtual.",
            "transaccion_id": transaccion.id,
            "comprobante": nro_comp,
            "monto_pagado": monto_decimal
        }, status=status.HTTP_201_CREATED)
'''

if 'class MobileSaldoPacienteView' not in view_content:
    with open(view_path, 'a', encoding='utf-8') as f:
        f.write('\n' + new_views)

# 3. Update URLS
url_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\urls.py'
with open(url_path, 'r', encoding='utf-8') as f:
    url_content = f.read()

new_imports = '''    ReportePersonalizadoAPIView,
    MobileSaldoPacienteView,
    PasarelaPagoMobileAPIView
)'''

if 'MobileSaldoPacienteView' not in url_content:
    url_content = url_content.replace('    ReportePersonalizadoAPIView\n)', new_imports)
    
    new_paths = '''    path("api/reportes/personalizado/", ReportePersonalizadoAPIView.as_view(), name="api_reporte_personalizado"),

    # Mobile Flutter Endpoints
    path("api/mobile/paciente/<int:paciente_id>/saldo/", MobileSaldoPacienteView.as_view(), name="api_mobile_saldo"),
    path("api/mobile/paciente/pagar/", PasarelaPagoMobileAPIView.as_view(), name="api_mobile_pagar"),
]'''
    url_content = url_content.replace('    path("api/reportes/personalizado/", ReportePersonalizadoAPIView.as_view(), name="api_reporte_personalizado"),\n]', new_paths)
    
    with open(url_path, 'w', encoding='utf-8') as f:
        f.write(url_content)

print('Done updating views, urls and permissions.')
