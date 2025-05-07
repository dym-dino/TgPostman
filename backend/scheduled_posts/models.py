"""
Scheduled post models
Models for storing scheduled posts and their attachments.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone

from chat_groups.models import ChatGroup
from telegram_accounts.models import TelegramChat


# --------------------------------------------------------------------------------


class ScheduledPost(models.Model):
    """
    Model representing a post scheduled for future publication.

    Attributes:
        user (User): The owner of the post.
        content (str): Text content of the post.
        html (bool): Whether the content is HTML.
        schedule_time (datetime): When to send the post.
        created_at (datetime): When the post was created.
        status (str): Current status of the post.
        error_message (str): Error info if sending failed.
        celery_task_id (str): ID of the Celery task.
        button_text (str): Optional inline button text.
        button_url (str): Optional inline button URL.
        targets (QuerySet): Selected individual chats.
        groups (QuerySet): Selected groups of chats.
    """

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent', 'Sent'),
        ('failed', 'Failed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    html = models.BooleanField(default=False)
    schedule_time = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    error_message = models.TextField(blank=True, null=True)
    celery_task_id = models.CharField(max_length=255, blank=True, null=True)

    button_text = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Текст inline-кнопки"
    )
    button_url = models.URLField(
        blank=True,
        null=True,
        help_text="URL inline-кнопки"
    )

    targets = models.ManyToManyField(
        TelegramChat,
        related_name='scheduled_posts',
        blank=True,
        help_text='Отдельные чаты/каналы'
    )
    groups = models.ManyToManyField(
        ChatGroup,
        related_name='scheduled_posts',
        blank=True,
        help_text='Группы чатов'
    )

    def save(self, *args, **kwargs) -> None:
        """
        Save the scheduled post, defaulting schedule_time if not set.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        if not self.schedule_time:
            self.schedule_time = timezone.now() + timedelta(minutes=1)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return string representation of the post.

        Returns:
            str: Summary of post author and schedule time.
        """
        return f"Post by {self.user.username} at {self.schedule_time}"

    def recipients(self):
        """
        Combine groups and targets into a single recipient list.

        Returns:
            list: All recipients (groups + targets).
        """
        return list(self.groups.all()) + list(self.targets.all())


# --------------------------------------------------------------------------------


class ScheduledPostAttachment(models.Model):
    """
    Model representing a file attached to a scheduled post.

    Attributes:
        post (ScheduledPost): Related scheduled post.
        file (File): Uploaded file.
        original_name (str): Name of the file at upload.
    """

    post = models.ForeignKey(
        ScheduledPost,
        related_name='attachments',
        on_delete=models.CASCADE
    )
    file = models.FileField(upload_to='uploads/')
    original_name = models.CharField(max_length=255)

    def __str__(self) -> str:
        """
        Return string representation of the attachment.

        Returns:
            str: Original filename and related post ID.
        """
        return f"{self.original_name} (post {self.post.id})"
