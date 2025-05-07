"""
Scheduled post serializer
Serializer for creating and validating scheduled posts with attachments.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import uuid
from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from chat_groups.models import ChatGroup
from telegram_accounts.models import TelegramChat
from .models import ScheduledPost, ScheduledPostAttachment
from .tasks import send_scheduled_post

# --------------------------------------------------------------------------------


class ScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and managing scheduled posts.

    Args:
        attachments (list[File]): Files to attach to the post.
        delay_seconds (int): Delay in seconds until scheduled time.
        schedule_time (datetime): Specific datetime to schedule the post.
        targets (list[int]): Telegram chat IDs.
        groups (list[int]): Chat group IDs.
        button_text (str): Optional inline button text.
        button_url (str): Optional inline button URL.

    Returns:
        ScheduledPost: Created post instance with attachments and schedule.
    """

    targets = serializers.PrimaryKeyRelatedField(queryset=TelegramChat.objects.all(), many=True)
    groups = serializers.PrimaryKeyRelatedField(queryset=ChatGroup.objects.all(), many=True)
    attachments = serializers.ListField(
        child=serializers.FileField(), write_only=True, required=False
    )
    delay_seconds = serializers.IntegerField(write_only=True, required=False)
    schedule_time = serializers.DateTimeField(required=False, write_only=True)
    button_text = serializers.CharField(required=False, allow_blank=True)
    button_url = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = ScheduledPost
        fields = (
            "id", "content", "html", "attachments", "targets", "groups",
            "schedule_time", "delay_seconds", "status", "created_at", "error_message",
            "button_text", "button_url"
        )
        read_only_fields = ("status", "created_at", "error_message", "schedule_time")

    def create(self, validated_data: dict) -> ScheduledPost:
        """
        Create a new ScheduledPost instance, assign attachments and schedule Celery task.

        Args:
            validated_data (dict): Validated data from request.

        Returns:
            ScheduledPost: Created and saved scheduled post.
        """
        attachments_data = validated_data.pop('attachments', [])
        delay = validated_data.pop('delay_seconds', None)
        schedule_time = validated_data.pop('schedule_time', None)
        btn_text = validated_data.pop('button_text', None)
        btn_url = validated_data.pop('button_url', None)
        user = self.context['request'].user
        targets = validated_data.pop('targets')
        groups = validated_data.pop('groups')

        post = ScheduledPost.objects.create(user=user, **validated_data)
        post.targets.set(targets)
        post.groups.set(groups)
        post.button_text = btn_text
        post.button_url = btn_url

        if schedule_time:
            if schedule_time < timezone.now():
                raise serializers.ValidationError("Время отправки должно быть в будущем!")
            post.schedule_time = schedule_time
        elif delay:
            post.schedule_time = timezone.now() + timedelta(seconds=delay)
        else:
            post.schedule_time = timezone.now()
        post.save()

        for f in attachments_data:
            original_name = f.name
            unique_name = f"{uuid.uuid4().hex}_{original_name}"
            f.name = unique_name
            ScheduledPostAttachment.objects.create(
                post=post,
                file=f,
                original_name=original_name
            )

        task = send_scheduled_post.apply_async(args=[post.id], eta=post.schedule_time)
        post.celery_task_id = task.id
        post.save()
        return post
