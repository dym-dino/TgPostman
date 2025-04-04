"""
API key authentication

This file contains the custom authentication class for API key authentication in the Django REST Framework.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import User


# --------------------------------------------------------------------------------
# AUTHENTICATION CLASS

class ApiKeyAuthentication(BaseAuthentication):
    """
    Custom authentication class that authenticates users based on an API key.
    """

    def authenticate(self, request):
        """
        Authenticate the user based on the provided API key.

        :param request: The HTTP request object containing the API key in the headers.
        :return: A tuple of user and None if the API key is valid, or raises AuthenticationFailed.
        """
        api_key = request.headers.get("X-API-KEY")
        if not api_key:
            return None

        try:
            user = User.objects.get(api_key=api_key)
        except User.DoesNotExist:
            raise AuthenticationFailed("Invalid API Key")

        return (user, None)
