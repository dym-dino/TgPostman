"""
Admin config

This file contains admin panel configuration for the ScheduledPost model.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib import admin

from .models import ScheduledPost

# --------------------------------------------------------------------------------
# ADMIN CONFIGURATION

@admin.register(ScheduledPost)
class PostAdmin(admin.ModelAdmin):
    """
    Admin configuration for displaying and managing ScheduledPost entries.
    """
    list_display = ('user', 'schedule_time', 'status', 'created_at')
    search_fields = ('user__username', 'content')
