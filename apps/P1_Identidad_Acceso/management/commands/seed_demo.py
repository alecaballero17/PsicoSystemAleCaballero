import os
from django.core.management.base import BaseCommand
from apps.P1_Identidad_Acceso.models import Usuario, Clinica
from apps.P2_Gestion_Clinica.models import Paciente, HistoriaClinica
from apps.P3_Logistica_Citas.models import Cita, ListaEspera

class Command(BaseCommand):
    help = 'Limpia la base de datos y crea usuarios de prueba (Sprints 0, 1, 2) para el Tribunal.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING("Iniciando limpieza profunda de la base de datos..."))
        
        # Eliminar en orden para respetar dependencias foráneas
        Cita.objects.all().delete()
        ListaEspera.objects.all().delete()
        HistoriaClinica.objects.all().delete()
        Paciente.objects.all().delete()
        Usuario.objects.all().delete()
        Clinica.objects.all().delete()
        
        self.stdout.write(self.style.SUCCESS("Base de datos limpia."))
        
        self.stdout.write(self.style.WARNING("Creando Súper Administrador Global..."))
        # CREAR SUPERADMIN
        Usuario.objects.create_superuser(username='superadmin', email='etsech67@gmail.com', password='Test12345', rol='ADMIN')

        self.stdout.write(self.style.WARNING("Creando Clínica 1: Centro Psicológico San Aurelio..."))
        # CREAR CLÍNICA 1
        c1 = Clinica.objects.create(nombre="Centro Psicológico San Aurelio", nit="111111", direccion="Av. San Aurelio", plan_suscripcion="Premium")
        
        # CLÍNICA 1 - ADMIN Y PSICOLOGO
        Usuario.objects.create_user(username='admin_aurelio', email='ramosvargabrayan@gmail.com', password='Test12345', rol='ADMIN', clinica=c1, debe_cambiar_password=False)
        Usuario.objects.create_user(username='psico_aurelio', email='joelramostrbj@gmail.com', password='Test12345', rol='PSICOLOGO', clinica=c1, especialidad='Terapia de Pareja', debe_cambiar_password=False)
        
        # CLÍNICA 1 - PACIENTES
        p1 = Paciente.objects.create(nombre="Carlos Dre", ci="888888", fecha_nacimiento="1995-01-01", telefono="7771111", clinica=c1)
        Usuario.objects.create_user(username='paciente_carlos', email='xdreicarlos@gmail.com', password='Test12345', rol='PACIENTE', clinica=c1, debe_cambiar_password=False)
        HistoriaClinica.objects.create(paciente=p1) # Expediente autogenerado
        
        p2 = Paciente.objects.create(nombre="Joe Toe", ci="999999", fecha_nacimiento="1990-05-05", telefono="7772222", clinica=c1)
        Usuario.objects.create_user(username='paciente_joe', email='joetoe250@gmail.com', password='Test12345', rol='PACIENTE', clinica=c1, debe_cambiar_password=False)
        HistoriaClinica.objects.create(paciente=p2)
        
        self.stdout.write(self.style.WARNING("Creando Clínica 2: Clínica Integral Mente Sana..."))
        # CREAR CLÍNICA 2
        c2 = Clinica.objects.create(nombre="Clínica Integral Mente Sana", nit="222222", direccion="Av. Bush", plan_suscripcion="Profesional")
        
        # CLÍNICA 2 - ADMIN Y PSICOLOGO
        Usuario.objects.create_user(username='admin_sana', email='si2psicologiaproy@gmail.com', password='Test12345', rol='ADMIN', clinica=c2, debe_cambiar_password=False)
        Usuario.objects.create_user(username='psico_sana', email='trabajodt1c0@gmail.com', password='Test12345', rol='PSICOLOGO', clinica=c2, especialidad='Ansiedad y Depresión', debe_cambiar_password=False)
        
        # CLÍNICA 2 - PACIENTES
        p3 = Paciente.objects.create(nombre="Fit Go", ci="555555", fecha_nacimiento="2000-10-10", telefono="7773333", clinica=c2)
        Usuario.objects.create_user(username='paciente_fit', email='fitgo61@gmail.com', password='Test12345', rol='PACIENTE', clinica=c2, debe_cambiar_password=False)
        HistoriaClinica.objects.create(paciente=p3)
        
        p4 = Paciente.objects.create(nombre="Joel Vargas", ci="666666", fecha_nacimiento="1998-12-12", telefono="7774444", clinica=c2)
        Usuario.objects.create_user(username='paciente_vargas', email='ramosvargasbrayanjoel66@gmail.com', password='Test12345', rol='PACIENTE', clinica=c2, debe_cambiar_password=False)
        HistoriaClinica.objects.create(paciente=p4)
        
        self.stdout.write(self.style.SUCCESS("\n========================================================"))
        self.stdout.write(self.style.SUCCESS("✅ DEMO DATA GENERADA EXITOSAMENTE!"))
        self.stdout.write(self.style.SUCCESS("✅ 2 Clínicas / 2 Administradores / 2 Psicólogos / 4 Pacientes"))
        self.stdout.write(self.style.SUCCESS("🔑 Contraseña universal para todos: Test12345"))
        self.stdout.write(self.style.SUCCESS("========================================================\n"))
