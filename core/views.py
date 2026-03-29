from django.shortcuts import render, redirect
from .forms import ClinicaForm
from django.contrib.auth.decorators import login_required # Importa el protector

@login_required # Protege la vista para que solo usuarios autenticados puedan acceder
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
    pass





from .forms import RegistroUsuarioForm # Asegúrate de importar el nuevo form

@login_required # Protege la vista para que solo usuarios autenticados puedan acceder
def registrar_usuario_view(request):
    # Lógica del CU02: Registro de Usuario/Psicólogo
    if request.method == 'POST':
        form = RegistroUsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('admin:index')
    else:
        form = RegistroUsuarioForm()
    
    return render(request, 'core/registrar_usuario.html', {'form': form})
    pass