from rest_framework import serializers
from .models import Transaccion, Comprobante

class TransaccionSerializer(serializers.ModelSerializer):
    paciente_nombre = serializers.ReadOnlyField(source='paciente.nombre')
    
    class Meta:
        model = Transaccion
        fields = [
            'id', 'paciente', 'paciente_nombre', 'monto', 
            'fecha', 'concepto', 'metodo_pago'
        ]
        read_only_fields = ['id', 'fecha']

class ComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = ['id', 'transaccion', 'nro_comprobante', 'pdf_archivo', 'fecha_emision']
        read_only_fields = ['id', 'fecha_emision']
