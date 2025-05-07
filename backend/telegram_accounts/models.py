"""
Telegram chat model
Model representing a Telegram chat or channel linked to a user.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.conf import settings
from django.db import models

# --------------------------------------------------------------------------------


class TelegramChat(models.Model):
    """
    Represents a Telegram chat or channel added by a user.

    Attributes:
        user (User): Owner of the chat entry.
        chat_id (int): Telegram chat ID.
        chat_type (str): Type of chat (group, channel, etc.).
        title (str): Display name of the chat.
        url (str): Optional public URL (t.me/…).
        can_post (bool): Whether the bot can post to this chat.
        added_at (datetime): Timestamp when the chat was added.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    chat_id = models.BigIntegerField()
    chat_type = models.CharField(max_length=32, blank=True)
    title = models.CharField(max_length=255)
    url = models.URLField(blank=True, null=True)
    can_post = models.BooleanField(default=False)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'chat_id')

    def __str__(self) -> str:
        """
        Return a user-friendly string representation of the chat.

        Returns:
            str: Formatted string with title, chat ID, and optional username.
        """
        return f"{self.title} ({self.chat_id} {'@' + self.url.replace('https://t.me/', '') if self.url else ''})"

    def __repr__(self) -> str:
        """
        Return an unambiguous string representation of the chat.

        Returns:
            str: Debug-friendly string with chat details.
        """
        return f"{self.title} ({self.chat_id} {'@' + self.url.replace('https://t.me/', '') if self.url else ''})"
