"""
WSGI config for psicosystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

print("wsgi.py: loading...", flush=True)

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psicosystem.settings')

application = get_wsgi_application()

print("wsgi.py: application loaded successfully.", flush=True)
