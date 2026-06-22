import os
import shutil
import datetime
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Realiza una copia de seguridad manual de la base de datos (SQLite)'

    def handle(self, *args, **kwargs):
        # Para el propósito de este proyecto, asumimos SQLite (db.sqlite3)
        db_path = settings.DATABASES['default'].get('NAME', 'db.sqlite3')
        
        if not os.path.exists(db_path):
            self.stdout.write(self.style.ERROR(f'No se encontro la base de datos en: {db_path}'))
            return

        backup_dir = os.path.join(settings.BASE_DIR, 'backups')
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)

        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_filename = f'backup_{timestamp}.sqlite3'
        backup_path = os.path.join(backup_dir, backup_filename)

        try:
            shutil.copy2(db_path, backup_path)
            self.stdout.write(self.style.SUCCESS(f'Backup creado exitosamente: {backup_path}'))
            self.stdout.write(self.style.SUCCESS(f'Para restaurar use: python manage.py restore_db {backup_filename}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creando el backup: {e}'))
