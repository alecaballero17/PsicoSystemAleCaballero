from django import forms
from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        fields = ['nombre', 'ci', 'fecha_nacimiento', 'telefono', 'motivo_consulta']
        labels = {
            'nombre': 'Nombre completo del paciente',
            'ci': 'Cédula de Identidad',
            'fecha_nacimiento': 'Fecha de nacimiento',
            'telefono': 'Teléfono/Celular',
            'motivo_consulta': 'Motivo de la consulta inicial',
        }
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'ci': forms.TextInput(attrs={'class': 'form-control'}),
            'fecha_nacimiento': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'motivo_consulta': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
