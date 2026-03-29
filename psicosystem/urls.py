from django.contrib import admin
from django.urls import path
from core.views import registrar_clinica_view, registrar_usuario_view, registrar_paciente_view # Importa la nueva vista para registrar pacientes
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin.site.urls),
    # Caso de Uso 01: Login
    path('login/', auth_views.LoginView.as_view(template_name='core/login.html'), name='login'),
    # Logout (Cerrar sesión)
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    
    path('registro-clinica/', registrar_clinica_view, name='registrar_clinica'),
    path('registro-psicologo/', registrar_usuario_view, name='registrar_psicologo'),
    path('registro-paciente/', registrar_paciente_view, name='registrar_paciente'),
]

