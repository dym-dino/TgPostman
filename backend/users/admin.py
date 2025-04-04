"""
User admin configuration

This file contains the admin configuration for managing User objects in the Django admin panel.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib import admin
from .models import User

# --------------------------------------------------------------------------------
# ADMIN CONFIGURATION

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """
    Admin configuration for the User model.
    """
    list_display = ('username', 'api_key', 'is_staff', 'is_active')
