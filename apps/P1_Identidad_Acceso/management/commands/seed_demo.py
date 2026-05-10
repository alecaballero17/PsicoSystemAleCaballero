import os
from django.core.management.base import BaseCommand
from apps.P1_Identidad_Acceso.models import Usuario, Clinica
from apps.P2_Gestion_Clinica.models import Paciente, HistoriaClinica
from apps.P3_Logistica_Citas.models import Cita, ListaEspera

class Command(BaseCommand):
    help = 'Limpia la base de datos y crea usuarios usando el EMAIL como USERNAME para facilidad del tribunal.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando limpieza profunda...")
        Cita.objects.all().delete()
        ListaEspera.objects.all().delete()
        HistoriaClinica.objects.all().delete()
        Paciente.objects.all().delete()
        Usuario.objects.all().delete()
        Clinica.objects.all().delete()
        
        # 1. SUPERADMIN
        admin_email = 'etsech67@gmail.com'
        admin = Usuario.objects.create_superuser(username=admin_email, email=admin_email)
        admin.set_password('Test12345')
        admin.rol = 'ADMIN'
        admin.debe_cambiar_password = False
        admin.save()

        # 2. CLÍNICA 1
        c1 = Clinica.objects.create(nombre="Centro Psicologico San Aurelio", nit="111111", direccion="Av. San Aurelio", plan_suscripcion="Premium")
        
        # Admin 1
        email_a1 = 'ramosvargabrayan@gmail.com'
        u1 = Usuario.objects.create_user(username=email_a1, email=email_a1)
        u1.set_password('Test12345')
        u1.rol = 'ADMIN'
        u1.clinica = c1
        u1.debe_cambiar_password = False
        u1.save()

        # Psico 1
        email_p1 = 'joelramostrbj@gmail.com'
        u2 = Usuario.objects.create_user(username=email_p1, email=email_p1)
        u2.set_password('Test12345')
        u2.rol = 'PSICOLOGO'
        u2.clinica = c1
        u2.especialidad = 'Terapia de Pareja'
        u2.debe_cambiar_password = False
        u2.save()
        
        # Pacientes Clínica 1
        pac_email1 = 'xdreicarlos@gmail.com'
        p1 = Paciente.objects.create(nombre="Carlos Dre", ci="888888", fecha_nacimiento="1995-01-01", telefono="7771111", clinica=c1)
        up1 = Usuario.objects.create_user(username=pac_email1, email=pac_email1)
        up1.set_password('Test12345')
        up1.rol = 'PACIENTE'
        up1.clinica = c1
        up1.debe_cambiar_password = False
        up1.save()
        HistoriaClinica.objects.create(paciente=p1)
        
        # 3. CLÍNICA 2
        c2 = Clinica.objects.create(nombre="Clinica Integral Mente Sana", nit="222222", direccion="Av. Bush", plan_suscripcion="Profesional")
        
        # Admin 2
        email_a2 = 'si2psicologiaproy@gmail.com'
        u3 = Usuario.objects.create_user(username=email_a2, email=email_a2)
        u3.set_password('Test12345')
        u3.rol = 'ADMIN'
        u3.clinica = c2
        u3.debe_cambiar_password = False
        u3.save()

        # Psico 2
        email_p2 = 'trabajodt1c0@gmail.com'
        u4 = Usuario.objects.create_user(username=email_p2, email=email_p2)
        u4.set_password('Test12345')
        u4.rol = 'PSICOLOGO'
        u4.clinica = c2
        u4.especialidad = 'Ansiedad y Depresion'
        u4.debe_cambiar_password = False
        u4.save()
        
        # Pacientes Clínica 2
        pac_email2 = 'fitgo61@gmail.com'
        p3 = Paciente.objects.create(nombre="Fit Go", ci="555555", fecha_nacimiento="2000-10-10", telefono="7773333", clinica=c2)
        up3 = Usuario.objects.create_user(username=pac_email2, email=pac_email2)
        up3.set_password('Test12345')
        up3.rol = 'PACIENTE'
        up3.clinica = c2
        up3.debe_cambiar_password = False
        up3.save()
        HistoriaClinica.objects.create(paciente=p3)
        
        self.stdout.write("✅ EXITO: Ahora puedes entrar usando tu EMAIL como USUARIO.")
        self.stdout.write("Password: Test12345")
