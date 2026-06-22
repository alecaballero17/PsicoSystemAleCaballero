#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Falso-aplicar migracion 0003 conflictiva porque la columna ya existe en la BD de Render
python manage.py migrate P1_Identidad_Acceso 0003_usuario_debe_cambiar_password_and_more --fake || true

# Ejecutar migraciones
python manage.py migrate

# Generar y comprimir recursos estáticos a través de WhiteNoise
python manage.py collectstatic --no-input
