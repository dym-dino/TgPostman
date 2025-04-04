"""
Telegram chat admin config

This file contains the admin configuration for managing Telegram chats in the Django admin panel.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib import admin

from .models import TelegramChat

# --------------------------------------------------------------------------------
# ADMIN CONFIGURATION

@admin.register(TelegramChat)
class TelegramChatAdmin(admin.ModelAdmin):
    """
    Admin configuration for the TelegramChat model, defining how Telegram chats are displayed and searched.
    """
    list_display = ('title', 'chat_id', 'user', 'can_post', 'added_at')
    search_fields = ('title', 'chat_id')
