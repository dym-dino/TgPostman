"""
Telegram chat serializer

This file defines the serializer for the TelegramChat model, including field definitions and object creation logic.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from rest_framework import serializers

from .models import TelegramChat


# --------------------------------------------------------------------------------
# SERIALIZER DEFINITION

class TelegramChatSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and displaying Telegram chat objects.
    """

    class Meta:
        model = TelegramChat
        fields = "__all__"
        read_only_fields = ("user", "title", "can_post", "chat_type", "url")

    def create(self, validated_data: dict) -> TelegramChat:
        """
        Create a new TelegramChat instance.

        :param validated_data: Validated data for creating a Telegram chat
        :return: The created TelegramChat instance
        """
        return TelegramChat.objects.create(**validated_data)
