"""
User API tests

This file contains tests for the user registration and API key generation, as well as verifying the API key functionality.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.urls import reverse
from rest_framework.test import APITestCase

from users.models import User

# --------------------------------------------------------------------------------
# TEST CASES

class UserTests(APITestCase):
    """
    Test case for user registration and API key generation.
    """

    def test_register_user_and_get_api_key(self) -> None:
        """
        Test the user registration and API key generation process.
        Verify that the user is created, and an API key is generated.
        """
        url = reverse("api_register")
        data = {
            "username": "testuser",
            "password": "TestPass1234"
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 201)

        # Retrieve the created user and verify the API key
        user = User.objects.get(username="testuser")
        self.assertIsNotNone(user.api_key)

        # Verify /me/ endpoint
        self.client.credentials(HTTP_X_API_KEY=user.api_key)
        response = self.client.get(reverse("api_key"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["username"], "testuser")
