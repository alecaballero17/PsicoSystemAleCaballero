from django.contrib import admin
from django.urls import path
from core.views import registrar_clinica_view # Importamos tu vista

urlpatterns = [
    # El error estaba en la línea de abajo, debe decir .urls NO .write
    path('admin/', admin.site.urls), 
    
    # Ruta para el Caso de Uso 25
    path('registro-clinica/', registrar_clinica_view, name='registrar_clinica'),
]