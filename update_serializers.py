import sys
from datetime import timedelta

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P3_Logistica_Citas\serializers.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Add timedelta import
if 'from datetime import timedelta' not in content:
    content = content.replace('from rest_framework import serializers', 'from rest_framework import serializers\nfrom datetime import timedelta')

# Add ListaEspera to models import
if 'ListaEspera' not in content:
    content = content.replace('from .models import Cita', 'from .models import Cita, ListaEspera')

# Add validation logic to CitaSerializer
validation_logic = '''
        fecha_hora = attrs.get("fecha_hora")
        if fecha_hora is None and self.instance:
            fecha_hora = self.instance.fecha_hora

        if psicologo and fecha_hora:
            # GAP-B1: Validar colisión (± 1 hora)
            hora_fin = fecha_hora + timedelta(hours=1)
            hora_inicio = fecha_hora - timedelta(hours=1)
            
            citas_cruzadas = Cita.objects.filter(
                psicologo=psicologo,
                fecha_hora__lt=hora_fin,
                fecha_hora__gt=hora_inicio,
                estado__in=['PENDIENTE', 'COMPLETADA']
            )
            
            if self.instance:
                citas_cruzadas = citas_cruzadas.exclude(id=self.instance.id)

            if citas_cruzadas.exists():
                raise serializers.ValidationError("El psicólogo ya tiene una cita en ese horario.")

        return attrs
'''
if 'citas_cruzadas' not in content:
    content = content.replace('        return attrs', validation_logic)

# Add ListaEsperaSerializer
lista_espera_serializer = '''
class ListaEsperaSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListaEspera
        fields = ["id", "paciente", "prioridad", "observacion", "fecha_registro", "activo"]

    def validate(self, attrs):
        request = self.context.get("request")
        user = getattr(request, "user", None)
        if not user or not user.is_authenticated or not user.clinica_id:
            raise serializers.ValidationError("Sesión o clínica no válida.")
        
        paciente = attrs.get("paciente")
        if paciente and paciente.clinica_id != user.clinica_id:
            raise serializers.ValidationError(
                {"paciente": "El paciente no pertenece a tu clínica."}
            )
        return attrs
'''
if 'class ListaEsperaSerializer' not in content:
    content += '\n' + lista_espera_serializer

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated serializers.py")
