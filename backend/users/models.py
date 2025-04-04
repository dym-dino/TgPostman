"""
Custom user model

This file defines the custom User model, extending the default AbstractUser model with an API key.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import secrets

from django.contrib.auth.models import AbstractUser
from django.db import models


# --------------------------------------------------------------------------------
# USER MODEL

class User(AbstractUser):
    """
    Custom user model that extends the default Django AbstractUser with an API key.
    """
    api_key = models.CharField(max_length=64, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs) -> None:
        """
        Override the save method to generate a new API key if it does not exist.

        :param args: Positional arguments passed to the parent save method
        :param kwargs: Keyword arguments passed to the parent save method
        """
        if not self.api_key:
            self.api_key = secrets.token_hex(32)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        """
        Return the string representation of the user, which is their username.

        :return: The user's username
        """
        return self.username
