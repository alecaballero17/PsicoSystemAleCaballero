import sys

file_path = r'C:\Users\personal\.gemini\antigravity\brain\a5bc1c34-45ae-44f8-b7e3-bf2b4c2dcf19\apps\P3_Logistica_Citas\views.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Imports needed
if 'from rest_framework import generics, viewsets, status' not in content:
    content = content.replace('from rest_framework import generics', 'from rest_framework import generics, viewsets, status\nfrom rest_framework.response import Response')

if 'from .models import Cita, ListaEspera' not in content:
    content = content.replace('from .models import Cita', 'from .models import Cita, ListaEspera')

if 'from .serializers import CitaSerializer, ListaEsperaSerializer' not in content:
    content = content.replace('from .serializers import CitaSerializer', 'from .serializers import CitaSerializer, ListaEsperaSerializer')


# GAP-B4: Modify CitaListCreateAPIView to add date filters
old_get_queryset = '''    def get_queryset(self):
        return (
            Cita.objects.filter(paciente__clinica=self.request.user.clinica)
            .select_related("paciente", "psicologo")
            .order_by("fecha_hora")
        )'''

new_get_queryset = '''    def get_queryset(self):
        queryset = Cita.objects.filter(paciente__clinica=self.request.user.clinica).select_related("paciente", "psicologo")
        
        # GAP-B4: Filtros de Calendario
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        psicologo_id = self.request.query_params.get('psicologo_id')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha_hora__date__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha_hora__date__lte=fecha_fin)
        if psicologo_id:
            queryset = queryset.filter(psicologo_id=psicologo_id)
            
        return queryset.order_by("fecha_hora")'''

if 'fecha_inicio = self.request.query_params.get' not in content:
    content = content.replace(old_get_queryset, new_get_queryset)

# GAP-B3: Change CitaRetrieveUpdateAPIView to RetrieveUpdateDestroyAPIView and add soft delete
content = content.replace('class CitaRetrieveUpdateAPIView(generics.RetrieveUpdateAPIView):', 'class CitaRetrieveUpdateAPIView(generics.RetrieveUpdateDestroyAPIView):')

soft_delete_logic = '''
    def perform_destroy(self, instance):
        # GAP-B3: Soft Delete para Citas
        instance.estado = 'CANCELADA'
        instance.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Canceló cita (API): id={instance.pk}"
        )
'''
if 'def perform_destroy' not in content:
    content += soft_delete_logic

# GAP-B2: Add ListaEsperaViewSet
lista_espera_viewset = '''
class ListaEsperaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para la Lista de Espera.
    """
    serializer_class = ListaEsperaSerializer
    permission_classes = [
        IsAuthenticated,
        EsPsicologoOAdministrador,
        HasClinicaAsignada,
    ]

    def get_queryset(self):
        return ListaEspera.objects.filter(
            paciente__clinica=self.request.user.clinica
        ).order_by('prioridad', 'fecha_registro')

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        espera = serializer.save()
        LogAuditoria.objects.create(
            usuario=self.request.user,
            accion=f"Añadió a lista de espera: {espera.paciente.nombre}"
        )
'''

if 'class ListaEsperaViewSet' not in content:
    content += '\n' + lista_espera_viewset

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated views.py")
