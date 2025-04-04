"""
User API URLs

This file defines the URL patterns for user-related API endpoints, including registration, login, and API key retrieval.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.urls import path
from .views import RegisterView, ApiKeyView, LoginAPIView

# --------------------------------------------------------------------------------
# URL PATTERNS

urlpatterns = [
    path('register/', RegisterView.as_view(), name='api_register'),
    path('me/', ApiKeyView.as_view(), name='api_key'),
    path('login_api/', LoginAPIView.as_view(), name='api_login'),
]
