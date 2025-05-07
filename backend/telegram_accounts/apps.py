"""
Telegram accounts config
App configuration for the telegram_accounts module.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.apps import AppConfig

# --------------------------------------------------------------------------------


class TelegramAccountsConfig(AppConfig):
    """
    Configuration class for the telegram_accounts application.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'telegram_accounts'
