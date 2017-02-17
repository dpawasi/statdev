"""
WSGI config for statdev project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import confy
from django.core.wsgi import get_wsgi_application
import os

confy.read_environment_file(".env")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statdev.settings")
application = get_wsgi_application()
