# Generated manually for SaaS Production Seeding

from django.db import migrations

def create_initial_plans(apps, schema_editor):
    PlanSuscripcion = apps.get_model('core', 'PlanSuscripcion')
    
    planes_data = [
        {
            "nombre": "BASIC",
            "descripcion": "Plan Básico (Consultorios Pequeños)",
            "max_pacientes": 50,
            "max_psicologos": 3,
            "precio_mensual": "29.99"
        },
        {
            "nombre": "PRO",
            "descripcion": "Plan Profesional (Clínicas Medianas)",
            "max_pacientes": 200,
            "max_psicologos": 10,
            "precio_mensual": "79.99"
        },
        {
            "nombre": "PREMIUM",
            "descripcion": "Plan Premium (Hospitales)",
            "max_pacientes": 1000,
            "max_psicologos": 50,
            "precio_mensual": "199.99"
        }
    ]
    
    for plan in planes_data:
        PlanSuscripcion.objects.get_or_create(
            nombre=plan["nombre"],
            defaults=plan
        )

def remove_plans(apps, schema_editor):
    PlanSuscripcion = apps.get_model('core', 'PlanSuscripcion')
    PlanSuscripcion.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_paciente_email'),
    ]

    operations = [
        migrations.RunPython(create_initial_plans, reverse_code=remove_plans),
    ]
