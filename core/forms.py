from django import forms
from .models import Clinica

class ClinicaForm(forms.ModelForm):
    class Meta:
        model = Clinica
        # Usamos los campos que definiste en tu modelo para el CU25
        fields = ['nombre', 'nit', 'plan_suscripcion']
        
        # Agregamos estilos de Bootstrap para que se vea bien
        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Centro Psicológico Ánima'}),
            'nit': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT de la institución'}),
            'plan_suscripcion': forms.Select(attrs={'class': 'form-select'}),
        }