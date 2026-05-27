#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Ejecutar migraciones
python manage.py migrate

# Generar y comprimir recursos estáticos a través de WhiteNoise
python manage.py collectstatic --no-input
