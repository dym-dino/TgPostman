"""
App config

This file contains application configuration for the scheduled_posts app.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.apps import AppConfig

# --------------------------------------------------------------------------------
# APPLICATION CONFIGURATION

class ScheduledPostsConfig(AppConfig):
    """
    Configuration class for the scheduled_posts Django app.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'scheduled_posts'
