#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🔥 [RENDER NUBE] Iniciando compilación de Servidor Django PsicoSystem"

# Crear directorio de logs dinámico para que FileHandler de Django no rompa
mkdir -p logs

# Instalar dependencias
pip install -r requirements.txt

# Generar y comprimir recursos estáticos a través de WhiteNoise
python manage.py collectstatic --no-input

# Ejecutar migraciones automáticas al clúster de Base de Datos PostgreSQL
python manage.py migrate

# Poblar base de datos con datos de demostración (idempotente)
echo "🌱 [RENDER NUBE] Poblando base de datos con clínicas y usuarios de demo..."
python manage.py seed_demo

echo "✅ [RENDER NUBE] Sistema compilado existosamente. ¡Listo para Gunicorn!"
