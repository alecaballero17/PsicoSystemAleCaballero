from django import forms

from .models import Cita
from apps.P1_Identidad_Acceso.models import Usuario


class CitaForm(forms.ModelForm):
    fecha_hora = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                "type": "datetime-local",
                "class": "form-control",
            }
        ),
        input_formats=["%Y-%m-%dT%H:%M"],
        label="Fecha y hora",
    )

    motivo = forms.CharField(
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        required=False,
        label="Motivo",
    )

    class Meta:
        model = Cita
        fields = ["paciente", "psicologo", "fecha_hora", "motivo", "estado"]
        widgets = {
            "paciente": forms.Select(attrs={"class": "form-select"}),
            "psicologo": forms.Select(attrs={"class": "form-select"}),
            "estado": forms.Select(attrs={"class": "form-select"}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)
        if user and getattr(user, "clinica_id", None):
            self.fields["psicologo"].queryset = Usuario.objects.filter(
                clinica_id=user.clinica_id, rol="PSICOLOGO"
            )
            self.fields["paciente"].queryset = self.fields["paciente"].queryset.filter(
                clinica_id=user.clinica_id
            )
        else:
            self.fields["psicologo"].queryset = Usuario.objects.none()
            self.fields["paciente"].queryset = self.fields["paciente"].queryset.none()
