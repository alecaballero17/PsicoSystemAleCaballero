import random
from datetime import datetime, timedelta
from django.core.management.base import BaseCommand
from apps.P1_Identidad_Acceso.models import Usuario, Clinica
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita
from apps.P4_IA_Administracion.models import Transaccion

class Command(BaseCommand):
    help = 'Semilla de datos realistas para PsicoSystem'

    def handle(self, *args, **kwargs):
        try:
            clinica = Clinica.objects.get(nombre='local')
        except Clinica.DoesNotExist:
            self.stdout.write(self.style.ERROR('Clínica "local" no encontrada.'))
            return

        # 1. Crear más pacientes
        nombres = ["Carlos Mendez", "Lucia Torres", "Mario Vargas", "Elena Rios", "Sebastian Paz", "Fabiana Luna", "Andrea Soliz", "Hugo Rocha"]
        pacientes_creados = []
        for nombre in nombres:
            p, created = Paciente.objects.get_or_create(
                ci=f"{random.randint(1000000, 9999999)}",
                defaults={
                    'nombre': nombre,
                    'clinica': clinica,
                    'telefono': f"7{random.randint(1000000, 9999999)}",
                    'fecha_nacimiento': "1990-05-15",
                    'motivo_consulta': "Consulta de prueba para reporte de IA."
                }
            )
            pacientes_creados.append(p)
        
        # 2. Crear nuevos psicólogos
        psicos_data = [
            ("psico.roberto", "Roberto", "Gomez", "Terapia Cognitiva"),
            ("psico.marta", "Marta", "Sanchez", "Psicoterapia Infantil")
        ]
        
        for username, fname, lname, esp in psicos_data:
            psico, created = Usuario.objects.get_or_create(
                username=username,
                defaults={
                    'first_name': fname,
                    'last_name': lname,
                    'email': f"{username}@clinica.com",
                    'rol': 'PSICOLOGO',
                    'clinica': clinica,
                    'especialidad': esp,
                    'telefono': f"7888{random.randint(1000, 9999)}",
                    'horario_atencion': "Lunes a Viernes 08:00 - 16:00"
                }
            )
            if created:
                psico.set_password("Psico123*")
                psico.save()

        psicologos = list(Usuario.objects.filter(rol='PSICOLOGO', clinica=clinica))
        
        # 3. Crear citas para los próximos 10 días
        hoy = datetime.now()
        estados = ['PENDIENTE', 'PENDIENTE', 'ASISTIO', 'REPROGRAMADA']
        motivos = ["Consulta de seguimiento", "Primera sesión", "Evaluación ansiedad", "Terapia de pareja", "Sesión de control"]
        
        citas_count = 0
        for i in range(25):
            paciente = random.choice(pacientes_creados)
            psicologo = random.choice(psicologos)
            dias_offset = random.randint(0, 10)
            hora = random.randint(8, 17)
            fecha_cita = hoy.replace(hour=hora, minute=0, second=0, microsecond=0) + timedelta(days=dias_offset)
            
            if not Cita.objects.filter(psicologo=psicologo, fecha_hora=fecha_cita).exists():
                Cita.objects.create(
                    paciente=paciente,
                    psicologo=psicologo,
                    fecha_hora=fecha_cita,
                    motivo=random.choice(motivos),
                    estado=random.choice(estados)
                )
                citas_count += 1

        # 4. Crear transacciones financieras
        conceptos = ["Consulta General", "Sesión Terapia", "Evaluación Psicométrica", "Terapia Grupal"]
        for i in range(15):
            paciente = random.choice(pacientes_creados)
            Transaccion.objects.create(
                clinica=clinica,
                paciente=paciente,
                monto=random.choice([150, 200, 250, 300, 400]),
                concepto=random.choice(conceptos)
            )

        self.stdout.write(self.style.SUCCESS(f'¡Éxito! Se crearon {len(pacientes_creados)} pacientes, {len(psicos_data)} psicólogos, {citas_count} citas y 15 transacciones.'))
