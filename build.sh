#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Falso-aplicar migraciones conflictivas si ya existen en la BD
python safe_migrate.py

# Generar y comprimir recursos estáticos a través de WhiteNoise
python manage.py collectstatic --no-input
