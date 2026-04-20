from django import forms
from .models import Clinica, Usuario
from django.contrib.auth.forms import UserCreationForm

class RegistroPsicologoCompletoForm(UserCreationForm):
    # Campos extra para la clínica
    nombre_clinica = forms.CharField(
        max_length=100, 
        label="Nombre del Consultorio/Clínica",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej. Centro Psicológico Ánima'})
    )
    nit_clinica = forms.CharField(
        max_length=20, 
        label="NIT",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'NIT de la institución'})
    )

    class Meta(UserCreationForm.Meta):
        model = Usuario
        # 'clinica' se asigna en la vista. UserCreationForm usa password1/password2 (no "password").
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})