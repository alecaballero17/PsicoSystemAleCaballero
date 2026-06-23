# Migration manual: Crea NotaClinica y ArchivoAdjunto vinculadas a HistoriaClinica
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('P2_Gestion_Clinica', '0007_remove_diagnosticopaciente_paciente_and_more'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='NotaClinica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contenido', models.TextField()),
                ('fecha', models.DateTimeField(auto_now_add=True)),
                ('expediente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='notas',
                    to='P2_Gestion_Clinica.historiaclinica',
                )),
                ('psicologo', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-fecha'],
            },
        ),
        migrations.CreateModel(
            name='ArchivoAdjunto',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('archivo', models.FileField(upload_to='expedientes/adjuntos/')),
                ('descripcion', models.CharField(blank=True, default='', max_length=255)),
                ('fecha_subida', models.DateTimeField(auto_now_add=True)),
                ('expediente', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='archivos',
                    to='P2_Gestion_Clinica.historiaclinica',
                )),
                ('subido_por', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    related_name='archivos_subidos',
                    to=settings.AUTH_USER_MODEL,
                )),
            ],
            options={
                'ordering': ['-fecha_subida'],
            },
        ),
    ]
