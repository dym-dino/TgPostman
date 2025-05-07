"""
Chat group serializers
Serializers for chat groups and their members.
"""

# --------------------------------------------------------------------------------

from rest_framework import serializers

from .models import ChatGroup, ChatGroupMember

# --------------------------------------------------------------------------------


class ChatGroupMemberSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a chat group member.

    Args:
        chat_id (int): Unique Telegram chat ID.
        language (str): Language of the chat.

    Returns:
        Serialized representation of ChatGroupMember.
    """

    class Meta:
        model = ChatGroupMember
        fields = ('id', 'chat_id', 'language')

# --------------------------------------------------------------------------------


class ChatGroupSerializer(serializers.ModelSerializer):
    """
    Serializer for representing a chat group with its members.

    Args:
        name (str): Name of the chat group.
        created_at (datetime): Creation timestamp.
        members (list): List of related ChatGroupMember objects.

    Returns:
        Serialized representation of ChatGroup with nested members.
    """

    members = ChatGroupMemberSerializer(many=True, read_only=True)

    class Meta:
        model = ChatGroup
        fields = ('id', 'name', 'created_at', 'members')
