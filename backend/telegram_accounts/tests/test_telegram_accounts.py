"""
Telegram chat tests

This file contains unit tests for the Telegram chat integration, including the add chat functionality.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from unittest.mock import patch
from django.urls import reverse
from rest_framework.test import APITestCase
from users.models import User

# --------------------------------------------------------------------------------
# TEST CASES

class TelegramChatTests(APITestCase):
    """
    Test case for testing the functionality related to Telegram chats.
    """
    def setUp(self) -> None:
        """
        Set up a test user and client credentials for the test cases.
        """
        self.user = User.objects.create_user(username="user1", password="1234")
        self.client.credentials(HTTP_X_API_KEY=self.user.api_key)

    @patch("telegram_accounts.views.get_chat_info")
    def test_add_chat(self, mock_get_chat_info) -> None:
        """
        Test the addition of a new Telegram chat using mocked chat info.
        :param mock_get_chat_info: Mock for the get_chat_info function.
        """
        mock_get_chat_info.return_value = {
            "title": "Test Group",
            "can_post": True,
            "chat_type": "channel",
            "url":None
        }
        data = {"chat_id": -100123456789}
        url = reverse("telegramchat-list")
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["title"], "Test Group")
