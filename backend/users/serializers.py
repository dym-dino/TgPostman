"""
User serializers

This file contains serializers for user registration and API key generation.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

# --------------------------------------------------------------------------------
# USER MODEL

UserModel = get_user_model()

# --------------------------------------------------------------------------------
# USER REGISTER SERIALIZER

class UserRegisterSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration, including password validation.
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = UserModel
        fields = ("username", "password")

    def create(self, validated_data: dict) -> UserModel:
        """
        Create a new user with the validated data.

        :param validated_data: Data that has passed validation
        :return: The newly created user
        """
        user = UserModel.objects.create(
            username=validated_data["username"],
            password=validated_data["password"]
        )
        return user

# --------------------------------------------------------------------------------
# API KEY SERIALIZER

class ApiKeySerializer(serializers.ModelSerializer):
    """
    Serializer for returning the user's username and API key.
    """
    class Meta:
        model = UserModel
        fields = ("username", "api_key")
