#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nusearch.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    import django
    django.setup()
    from channels.routing import get_default_application
    application = get_default_application()
    
    # For example, run an ASGI server (using uvicorn here)
    import uvicorn
    uvicorn.run(application, host="0.0.0.0", port=8000)


if __name__ == '__main__':
    main()
