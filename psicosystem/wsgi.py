"""
WSGI config for psicosystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os

# Parche para evitar error de "drf_format_suffix already registered" en Django 5/6+
# Necesario aquí porque Gunicorn carga wsgi.py directamente (no pasa por manage.py)
try:
    import django.urls
    import django.urls.converters
    _original_register_converter = django.urls.converters.register_converter
    def _patched_register_converter(converter, type_name):
        try:
            _original_register_converter(converter, type_name)
        except ValueError as e:
            if "already registered" in str(e):
                pass
            else:
                raise
    django.urls.register_converter = _patched_register_converter
    django.urls.converters.register_converter = _patched_register_converter
except Exception:
    pass

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psicosystem.settings')

application = get_wsgi_application()
