import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.P1_Identidad_Acceso.models import Clinica, Usuario
from apps.P2_Gestion_Clinica.models import Paciente, HistoriaClinica

class Command(BaseCommand):
    help = 'Puebla la base de datos con 3 clínicas de prueba (Basico, Profesional, Premium) y datos de ejemplo.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando Data Seeding para Demostración SaaS...")

        # 1. Crear Clínicas
        planes = [
            ("Basico", "Clínica Esperanza", "Av. Siempre Viva 123"),
            ("Profesional", "Centro Médico Salud Mental", "Calle de la Paz 456"),
            ("Premium", "Instituto Psiquiátrico Global", "Torre Empresarial, Piso 10")
        ]

        clinicas_creadas = []
        for plan, nombre, dir in planes:
            clinica, created = Clinica.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "nit": f"100200{random.randint(100, 999)}",
                    "direccion": dir,
                    "plan_suscripcion": plan
                }
            )
            clinicas_creadas.append(clinica)
            self.stdout.write(self.style.SUCCESS(f"Clínica {'creada' if created else 'existente'}: {nombre} ({plan})"))

        # 2. Crear Administradores, Psicólogos y Pacientes para cada Clínica
        for clinica in clinicas_creadas:
            plan = clinica.plan_suscripcion
            prefijo = plan.lower()

            # Administrador
            admin_user, admin_created = Usuario.objects.get_or_create(
                username=f"admin.{prefijo}",
                defaults={
                    "email": f"admin@{prefijo}.com",
                    "password": make_password("Password123"),
                    "first_name": "Gerente",
                    "last_name": plan,
                    "rol": "ADMIN",
                    "clinica": clinica
                }
            )

            # Psicólogos (Basico=1, Profesional=3, Premium=5)
            num_psico = 1 if plan == "Basico" else 3 if plan == "Profesional" else 5
            for i in range(num_psico):
                Usuario.objects.get_or_create(
                    username=f"psico{i+1}.{prefijo}",
                    defaults={
                        "email": f"psico{i+1}@{prefijo}.com",
                        "password": make_password("Password123"),
                        "first_name": f"Doctor {i+1}",
                        "last_name": "Pérez",
                        "rol": "PSICOLOGO",
                        "clinica": clinica
                    }
                )

            # Pacientes
            num_pacientes = 2 if plan == "Basico" else 5
            for i in range(num_pacientes):
                paciente, pac_created = Paciente.objects.get_or_create(
                    ci=f"{random.randint(1000000, 9999999)}",
                    defaults={
                        "nombre": f"Paciente de Prueba {i+1} ({plan})",
                        "fecha_nacimiento": "1990-01-01",
                        "telefono": f"7000000{i}",
                        "clinica": clinica
                    }
                )
                if pac_created:
                    HistoriaClinica.objects.get_or_create(paciente=paciente)

            # Paciente Usuario para la app móvil (solo 1 por clínica para probar el login)
            Usuario.objects.get_or_create(
                username=f"paciente@{prefijo}.com",
                defaults={
                    "email": f"paciente@{prefijo}.com",
                    "password": make_password("Password123"),
                    "first_name": "Paciente",
                    "last_name": "Móvil",
                    "rol": "PACIENTE",
                    "clinica": clinica
                }
            )

        self.stdout.write(self.style.SUCCESS("¡Seeding completado! Datos listos para la demostración."))
