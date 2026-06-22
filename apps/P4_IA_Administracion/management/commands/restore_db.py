import os
import shutil
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Restaura una copia de seguridad manual de la base de datos (SQLite)'

    def add_arguments(self, parser):
        parser.add_argument('backup_filename', type=str, help='Nombre del archivo en la carpeta backups')

    def handle(self, *args, **options):
        filename = options['backup_filename']
        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        backup_path = os.path.join(backup_dir, filename)

        if not os.path.exists(backup_path):
            self.stdout.write(self.style.ERROR(f'No se encontro el archivo de backup en: {backup_path}'))
            return

        db_path = settings.DATABASES['default'].get('NAME', 'db.sqlite3')
        
        # Opcional: Crear un backup rapido de seguridad antes de sobreescribir
        if os.path.exists(db_path):
            shutil.copy2(db_path, f"{db_path}.temp_pre_restore")
            self.stdout.write(self.style.WARNING('Se creo un backup temporal (db.sqlite3.temp_pre_restore) de la DB actual por si acaso.'))

        try:
            shutil.copy2(backup_path, db_path)
            self.stdout.write(self.style.SUCCESS(f'Restauracion exitosa desde: {backup_path}'))
            self.stdout.write(self.style.SUCCESS('La base de datos ha sido reemplazada. Por favor, reinicie el servidor.'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error restaurando el backup: {e}'))
