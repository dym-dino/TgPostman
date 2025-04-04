"""
Telegram chat URLs

This file defines the URL patterns for managing Telegram chats via both web and API interfaces.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TelegramChatListCreateView,
    TelegramChatDeleteView,
    add_chat_view,
    TelegramChatViewSet,
)

# --------------------------------------------------------------------------------
# ROUTER SETUP

router = DefaultRouter()
router.register(r'chats', TelegramChatViewSet, basename='telegramchat')

# --------------------------------------------------------------------------------
# URL PATTERNS

urlpatterns = [
    # Web interface
    path('my-chats/', TelegramChatListCreateView.as_view(), name='my_chats'),
    path('add/', add_chat_view, name='add_chat'),
    path('manage/', TelegramChatListCreateView.as_view(), name='manage_telegram_chats'),
    path('delete/<int:pk>/', TelegramChatDeleteView.as_view(), name='delete_telegram_chat'),

    # API
    path('', include(router.urls)),
]
