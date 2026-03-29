from django.shortcuts import render, redirect
from .forms import ClinicaForm

def registrar_clinica_view(request):
    # Lógica del Caso de Uso 25: Registro de Clínicas
    if request.method == 'POST':
        form = ClinicaForm(request.POST)
        if form.is_valid():
            form.save()
            # Una vez creada, redirigimos al admin para ver que se guardó
            return redirect('admin:index') 
    else:
        form = ClinicaForm()
    
    return render(request, 'core/registrar_clinica.html', {'form': form})