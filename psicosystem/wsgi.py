"""
WSGI config for psicosystem project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
import sys
import traceback

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

_django_app = get_wsgi_application()


def application(environ, start_response):
    """
    Thin WSGI wrapper that catches any unhandled exception during request
    processing and writes a full traceback to stderr so it appears in the
    Railway / Gunicorn log stream.  Without this, Django can fail silently
    and the worker returns an empty response with no log output.
    """
    try:
        return _django_app(environ, start_response)
    except Exception:
        # Log the full traceback to stderr (visible in Railway logs).
        print("WSGI ERROR — unhandled exception during request processing:",
              file=sys.stderr, flush=True)
        traceback.print_exc(file=sys.stderr)
        sys.stderr.flush()

        # Return a plain 500 so the client gets a proper HTTP response
        # instead of a connection reset / "Application failed to respond".
        start_response(
            "500 Internal Server Error",
            [("Content-Type", "text/plain; charset=utf-8")],
        )
        return [b"Internal Server Error\n"]
