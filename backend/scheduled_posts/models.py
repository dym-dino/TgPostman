"""
Scheduled post model

This file defines the ScheduledPost model, which represents a post scheduled for future delivery.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from telegram_accounts.models import TelegramChat

# --------------------------------------------------------------------------------
# MODEL DEFINITION

class ScheduledPost(models.Model):
    """
    Model representing a post scheduled to be sent to Telegram chats.
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    html = models.BooleanField(default=False)
    file = models.FileField(upload_to='uploads/', blank=True, null=True)
    targets = models.ManyToManyField(TelegramChat)
    schedule_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    def save(self, *args, **kwargs) -> None:
        """
        Override the default save method to set a default schedule time if none is provided.
        """
        if not self.schedule_time:
            self.schedule_time = timezone.now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return a string representation of the post.
        :return: Post description including username and scheduled time.
        """
        return f"Post by {self.user.username} at {self.schedule_time}"
