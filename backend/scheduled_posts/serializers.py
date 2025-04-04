"""
Scheduled post serializer

This file defines a serializer for the ScheduledPost model, supporting optional delays and Celery task scheduling.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.utils import timezone
from rest_framework import serializers

from telegram_accounts.models import TelegramChat
from .models import ScheduledPost
from .tasks import send_scheduled_post


# --------------------------------------------------------------------------------
# SERIALIZER DEFINITION

class ScheduledPostSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and displaying ScheduledPost instances.
    Supports delay in seconds and triggers Celery task scheduling.
    """
    targets = serializers.PrimaryKeyRelatedField(queryset=TelegramChat.objects.all(), many=True)
    delay_seconds = serializers.IntegerField(write_only=True, required=False)
    schedule_time = serializers.DateTimeField(required=False, write_only=True)
    file = serializers.FileField(required=False, allow_null=True)

    class Meta:
        model = ScheduledPost
        fields = (
            "id", "content", "html", "file", "targets",
            "schedule_time", "delay_seconds", "status", "created_at", "error_message"
        )
        read_only_fields = ("status", "created_at", "error_message", "schedule_time")

    def create(self, validated_data: dict) -> ScheduledPost:
        """
        Create a ScheduledPost instance, apply delay if provided, and schedule a Celery task.

        :param validated_data: Validated input data
        :return: ScheduledPost instance
        """
        delay = validated_data.pop("delay_seconds", None)
        schedule_time = validated_data.pop("schedule_time", None)
        user = self.context["request"].user
        targets = validated_data.pop("targets")
        post = ScheduledPost.objects.create(user=user, **validated_data)
        post.targets.set(targets)

        if schedule_time:
            if schedule_time < timezone.now():
                raise serializers.ValidationError("Время отправки должно быть в будущем!")
            post.schedule_time = schedule_time
        elif delay:
            post.schedule_time = timezone.now() + timezone.timedelta(seconds=delay)
        else:
            post.schedule_time = timezone.now()

        task = send_scheduled_post.apply_async(args=[post.id], eta=post.schedule_time)
        post.celery_task_id = task.id
        post.save()

        return post
