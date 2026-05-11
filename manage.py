import os
import sys

# Parche para evitar error de "drf_format_suffix already registered" en Django 5/6+
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

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psicosystem.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
