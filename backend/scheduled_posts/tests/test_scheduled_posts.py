"""
Post tests

This file contains unit tests for post creation with delay using Django REST Framework and Celery.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from unittest.mock import patch

from django.urls import reverse
from rest_framework.test import APITestCase

from telegram_accounts.models import TelegramChat
from users.models import User


# --------------------------------------------------------------------------------
# TEST CASES

class PostTests(APITestCase):
    """
    Test case for creating posts with delayed execution via Celery.
    """

    def setUp(self) -> None:
        """
        Set up a test user and a Telegram chat for use in test methods.
        """
        self.user: User = User.objects.create_user(username="user2", password="pass")
        self.client.credentials(HTTP_X_API_KEY=self.user.api_key)
        self.chat: TelegramChat = TelegramChat.objects.create(
            user=self.user,
            chat_id=-123456789,
            title="Test Chat",
            can_post=True
        )

    @patch("scheduled_posts.tasks.send_scheduled_post.apply_async")
    def test_create_post_with_delay(self, mock_async: patch) -> None:
        """
        Test creating a post with a delay. Verifies that Celery async task is triggered.
        :param mock_async: Mock for Celery apply_async method
        """
        data: dict = {
            "content": "Hello!",
            "html": True,
            "targets": [self.chat.id],
            "delay_seconds": 60
        }

        response = self.client.post(reverse("posts"), data)

        self.assertEqual(response.status_code, 201)
        self.assertTrue(mock_async.called)
