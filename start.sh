#!/usr/bin/env bash

echo "🔥 [STARTUP NUBE] Iniciando servidor Gunicorn y preparando tareas de fondo..."

# Lanzar operaciones de base de datos en segundo plano. Esto permite que Gunicorn responda de inmediato
# al Health Check de Render, forzando la desactivación del contenedor antiguo (liberando bloqueos de DB)
# y luego aplicando las migraciones y semillas sobre la DB libre de locks.
(
    echo "⏱️ [DATABASE NUBE] Esperando 15 segundos para la estabilización del contenedor..."
    sleep 15
    
    # ELIMINADO: python manage.py flush --no-input (Esto borraba TODA tu base de datos al iniciar el servidor)
    
    echo "🔥 [DATABASE NUBE] Ejecutando migraciones..."
    python manage.py migrate --no-input || echo "⚠️ Advertencia: Error en las migraciones."
    
    # ELIMINADO: python manage.py seed_demo (Esto sobreescribía con datos de prueba)
    
    echo "✅ [DATABASE NUBE] Operaciones de base de datos finalizadas con éxito!"
) &

echo "🚀 [STARTUP NUBE] Iniciando Gunicorn de inmediato..."
exec gunicorn psicosystem.wsgi:application
