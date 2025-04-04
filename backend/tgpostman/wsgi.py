"""
WSGI configuration

This file configures the WSGI application for the project.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import os
from django.core.wsgi import get_wsgi_application

# --------------------------------------------------------------------------------
# WSGI APPLICATION SETUP

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgpostman.settings')

application = get_wsgi_application()
