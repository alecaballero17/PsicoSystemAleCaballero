import os
import django
import random
from datetime import datetime, timedelta

import sys
# Configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'PsicoSystem_SI2.settings')
sys.path.append(os.getcwd())
django.setup()

from apps.P1_Identidad_Acceso.models import Usuario, Clinica
from apps.P2_Gestion_Clinica.models import Paciente
from apps.P3_Logistica_Citas.models import Cita
from apps.P4_IA_Administracion.models import Transaccion

def populate_data():
    clinica = Clinica.objects.get(nombre='local')
    
    # 1. Crear más pacientes
    nombres = ["Carlos Mendez", "Lucia Torres", "Mario Vargas", "Elena Rios", "Sebastian Paz", "Fabiana Luna"]
    pacientes_creados = []
    for nombre in nombres:
        p, created = Paciente.objects.get_or_create(
            nombre=nombre,
            clinica=clinica,
            defaults={
                'email': f"{nombre.lower().replace(' ', '.')}@test.com",
                'telefono': f"7{random.randint(1000000, 9999999)}",
                'direccion': "Calle Falsa 123",
                'fecha_nacimiento': "1990-05-15"
            }
        )
        pacientes_creados.append(p)
    
    # 2. Crear un nuevo psicólogo
    psico_nuevo, created = Usuario.objects.get_or_create(
        username="psico.roberto",
        defaults={
            'first_name': "Roberto",
            'last_name': "Gomez",
            'email': "roberto@clinica.com",
            'rol': 'PSICOLOGO',
            'clinica': clinica,
            'especialidad': "Terapia Cognitivo Conductual",
            'telefono': "78881234",
            'horario_atencion': "Lunes a Viernes 08:00 - 14:00"
        }
    )
    if created:
        psico_nuevo.set_password("Psico123*")
        psico_nuevo.save()
    
    psicologos = list(Usuario.objects.filter(rol='PSICOLOGO', clinica=clinica))
    
    # 3. Crear citas para los próximos 7 días
    hoy = datetime.now()
    estados = ['PENDIENTE', 'PENDIENTE', 'ASISTIO', 'REPROGRAMADA']
    motivos = ["Consulta de seguimiento", "Primera sesión", "Evaluación ansiedad", "Terapia de pareja"]
    
    for i in range(15):
        paciente = random.choice(pacientes_creados)
        psicologo = random.choice(psicologos)
        dias_offset = random.randint(0, 7)
        hora = random.randint(8, 18)
        fecha_cita = hoy.replace(hour=hora, minute=0, second=0, microsecond=0) + timedelta(days=dias_offset)
        
        # Evitar duplicados exactos para el mismo psicólogo
        if not Cita.objects.filter(psicologo=psicologo, fecha_hora=fecha_cita).exists():
            Cita.objects.create(
                paciente=paciente,
                psicologo=psicologo,
                fecha_hora=fecha_cita,
                motivo=random.choice(motivos),
                estado=random.choice(estados)
            )

    # 4. Crear transacciones financieras
    conceptos = ["Consulta General", "Sesión Terapia", "Evaluación Psicométrica"]
    for i in range(10):
        paciente = random.choice(pacientes_creados)
        Transaccion.objects.create(
            paciente=paciente,
            monto=random.choice([150, 200, 300, 500]),
            concepto=random.choice(conceptos),
            fecha=hoy - timedelta(days=random.randint(0, 15))
        )

    print("¡Datos inyectados con éxito!")

if __name__ == "__main__":
    populate_data()
