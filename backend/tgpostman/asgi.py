"""
ASGI configuration

This file configures the ASGI application for the project.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import os

from django.core.asgi import get_asgi_application

# --------------------------------------------------------------------------------
# ASGI APPLICATION SETUP

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgpostman.settings')

application = get_asgi_application()
