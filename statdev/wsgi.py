"""
WSGI config for statdev project.
It exposes the WSGI callable as a module-level variable named ``application``.
"""
import confy
import os
from django.core.wsgi import get_wsgi_application

confy.read_environment_file()
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "statdev.settings")
application = get_wsgi_application()
