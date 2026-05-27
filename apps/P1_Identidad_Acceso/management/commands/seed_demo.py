import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from apps.P1_Identidad_Acceso.models import Clinica, Usuario
from apps.P2_Gestion_Clinica.models import Paciente, ExpedienteClinico
from apps.P4_IA_Administracion.models import LogAuditoria
from apps.P3_Logistica_Citas.models import Cita

class Command(BaseCommand):
    help = 'Puebla la base de datos con 4 clínicas de prueba (Basico, Profesional, Premium, Premium-Vacia) y datos de ejemplo.'

    def handle(self, *args, **kwargs):
        self.stdout.write("Iniciando Data Seeding para Demostración SaaS...")

        # 1. Crear Clínicas
        planes = [
            ("Basico", "Clínica Esperanza", "Av. Siempre Viva 123", 2),
            ("Profesional", "Centro Médico Salud Mental", "Calle de la Paz 456", 2),
            ("Premium", "Instituto Psiquiátrico Global", "Torre Empresarial, Piso 10", 3),
            ("Premium", "Clínica Premium Vacía", "Sin psicólogos 000", 0)  # La 4ta clínica sin psicólogos
        ]

        clinicas_creadas = []
        for plan, nombre, direccion, num_psico in planes:
            clinica, created = Clinica.objects.get_or_create(
                nombre=nombre,
                defaults={
                    "nit": f"100200{random.randint(100, 999)}",
                    "direccion": direccion,
                    "plan_suscripcion": plan
                }
            )
            clinicas_creadas.append((clinica, num_psico))
            self.stdout.write(self.style.SUCCESS(f"Clínica {'creada' if created else 'existente'}: {nombre} ({plan})"))

        # 2. Crear Administradores, Psicólogos y Pacientes para cada Clínica
        for i, (clinica, num_psico) in enumerate(clinicas_creadas):
            plan = clinica.plan_suscripcion
            prefijo = f"clinica{i+1}"

            # Administrador
            admin_user, admin_created = Usuario.objects.get_or_create(
                username=f"admin.{prefijo}",
                defaults={
                    "email": f"admin@{prefijo}.com",
                    "password": make_password("Password123"),
                    "first_name": "Gerente",
                    "last_name": clinica.nombre,
                    "rol": "ADMIN",
                    "clinica": clinica
                }
            )

            # Psicólogos
            for j in range(num_psico):
                Usuario.objects.get_or_create(
                    username=f"psico{j+1}.{prefijo}",
                    defaults={
                        "email": f"psico{j+1}@{prefijo}.com",
                        "password": make_password("Password123"),
                        "first_name": f"Doctor {j+1}",
                        "last_name": "Pérez",
                        "rol": "PSICOLOGO",
                        "clinica": clinica
                    }
                )

            # Pacientes
            num_pacientes = 3 if num_psico > 0 else 0
            for k in range(num_pacientes):
                paciente, pac_created = Paciente.objects.get_or_create(
                    ci=f"{random.randint(1000000, 9999999)}",
                    defaults={
                        "nombre": f"Paciente {k+1} ({clinica.nombre})",
                        "fecha_nacimiento": "1990-01-01",
                        "telefono": f"7000000{k}",
                        "clinica": clinica
                    }
                )
                if pac_created:
                    ExpedienteClinico.objects.get_or_create(paciente=paciente)

            # Paciente Usuario para la app móvil
            if num_psico > 0:
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

            # Auditoría simple
            LogAuditoria.objects.get_or_create(
                usuario=admin_user, 
                accion="Configuración inicial del sistema completada."
            )

            # Citas aleatorias
            psicologos = Usuario.objects.filter(clinica=clinica, rol="PSICOLOGO")
            pacientes_list = Paciente.objects.filter(clinica=clinica)
            
            if psicologos.exists() and pacientes_list.exists():
                for k in range(4):
                    Cita.objects.get_or_create(
                        paciente=random.choice(pacientes_list),
                        psicologo=random.choice(psicologos),
                        fecha_hora=datetime.now() + timedelta(days=k, hours=random.randint(1, 4)),
                        defaults={"motivo": "Consulta de Seguimiento", "estado": "PENDIENTE"}
                    )

        self.stdout.write(self.style.SUCCESS("¡Seeding completado! Datos listos para la demostración."))
