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

    Attributes:
        list_display (tuple): Fields to display in the list view.
        search_fields (tuple): Fields to use in the admin search.
    """
    list_display = ('user', 'schedule_time', 'status', 'created_at')
    search_fields = ('user__username', 'content')
