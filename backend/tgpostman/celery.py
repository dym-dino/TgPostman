"""
Celery configuration

This file sets up the Celery application for the project.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import os
from celery import Celery

# --------------------------------------------------------------------------------
# CELERY APP SETUP

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tgpostman.settings')
app = Celery('tgpostman')

# Configure Celery to use Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Automatically discover tasks in the project
app.autodiscover_tasks()

# Celery timezone settings
app.conf.enable_utc = True
app.conf.timezone = 'Europe/Moscow'
