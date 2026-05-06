from rest_framework import serializers
from .models import Transaccion, Comprobante

class TransaccionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaccion
        fields = ['id', 'paciente', 'monto', 'tipo', 'fecha', 'descripcion']

class ComprobanteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comprobante
        fields = ['id', 'transaccion', 'nro_comprobante', 'fecha_emision', 'pdf_path']
