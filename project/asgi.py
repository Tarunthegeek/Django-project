"""ASGI config for the privacy-preserving AI deployment project."""
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
application = get_asgi_application()
