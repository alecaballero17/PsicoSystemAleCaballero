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


from django.contrib.auth.forms import UserCreationForm
from .models import Usuario, Clinica

# core/forms.py

class RegistroUsuarioForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ['username', 'email', 'first_name', 'last_name', 'clinica', 'rol']
        # Aquí personalizamos los nombres que se ven en pantalla
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombres',
            'last_name': 'Apellidos',
            'clinica': 'Clínica asignada',
            'rol': 'Rol del usuario',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})


from .models import Paciente

class PacienteForm(forms.ModelForm):
    class Meta:
        model = Paciente
        # Campos básicos según el documento
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