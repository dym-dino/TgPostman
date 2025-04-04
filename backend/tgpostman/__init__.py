"""
Celery app initialization

This file initializes the Celery app and exposes it for use in the project.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from .celery import app as celery_app

# --------------------------------------------------------------------------------
# CELERY APP EXPORT

__all__ = ['celery_app']
