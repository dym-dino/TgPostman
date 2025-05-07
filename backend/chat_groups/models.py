"""
Chat group models
Models for grouping and managing Telegram chats.
"""

# --------------------------------------------------------------------------------

from django.conf import settings
from django.db import models

from tgpostman.settings import LANG_CHOICES

# --------------------------------------------------------------------------------


class ChatGroup(models.Model):
    """
    Represents a group of Telegram chats linked to a specific user.

    Args:
        user (User): The owner of the chat group.
        name (str): The name of the group.
        created_at (datetime): Timestamp of group creation.

    Returns:
        ChatGroup instance representing a user-defined group of chats.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='chat_groups'
    )
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'name')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.user.username})'

# --------------------------------------------------------------------------------


class ChatGroupMember(models.Model):
    """
    Represents a Telegram chat added to a specific chat group.

    Args:
        group (ChatGroup): The group this member belongs to.
        chat_id (int): Unique Telegram chat ID.
        language (str): Language of the chat (from LANG_CHOICES).

    Returns:
        ChatGroupMember instance representing a group-chat relationship.
    """

    group = models.ForeignKey(
        ChatGroup,
        related_name='members',
        on_delete=models.CASCADE
    )
    chat_id = models.BigIntegerField()
    language = models.CharField(max_length=10, choices=LANG_CHOICES)

    class Meta:
        unique_together = ('group', 'chat_id')

    def __str__(self):
        return f'{self.chat_id} in {self.group.name} ({self.language})'
