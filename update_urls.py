import os
import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P4_IA_Administracion\urls.py'

with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the import block
old_import = '''from .views import (
    DashboardAPIView, 
    LogAuditoriaAPIView, 
    AnalisisIAView,
    TransaccionViewSet,
    SaldoPacienteView,
    GenerarComprobantePDFView
)'''

new_import = '''from .views import (
    DashboardAPIView, 
    LogAuditoriaAPIView, 
    AnalisisIAView,
    TransaccionViewSet,
    SaldoPacienteView,
    GenerarComprobantePDFView,
    ReportePersonalizadoAPIView
)'''

content = content.replace(old_import, new_import)

# Append the new path
if 'api/reportes/personalizado/' not in content:
    content = content.replace(
        'path("api/finanzas/comprobante/<int:transaccion_id>/pdf/", GenerarComprobantePDFView.as_view(), name="api_comprobante_pdf"),\n]',
        'path("api/finanzas/comprobante/<int:transaccion_id>/pdf/", GenerarComprobantePDFView.as_view(), name="api_comprobante_pdf"),\n    path("api/reportes/personalizado/", ReportePersonalizadoAPIView.as_view(), name="api_reporte_personalizado"),\n]'
    )

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
print('Done updating urls.py')
