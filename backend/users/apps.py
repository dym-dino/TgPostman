"""
Users app configuration

This file contains the configuration for the 'users' Django app.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.apps import AppConfig

# --------------------------------------------------------------------------------
# APP CONFIGURATION

class UsersConfig(AppConfig):
    """
    Configuration for the 'users' app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
