"""
URL configuration for tgpostman project.

This file contains the URL patterns for the web interface, API modules, and documentation.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path, include
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions
from django.conf import settings
from django.conf.urls.static import static
from users.views import register_view, dashboard_view

# --------------------------------------------------------------------------------
# SCHEMA VIEW SETUP

schema_view = get_schema_view(
    openapi.Info(
        title="TgPostman API",
        default_version='v1',
        description="Система отложенного постинга в Telegram",
        contact=openapi.Contact(email="support@tgpostman.com"),
        license=openapi.License(name="MIT License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

# --------------------------------------------------------------------------------
# URL PATTERNS

urlpatterns = [
    path('admin/', admin.site.urls),

    # Web interface
    path('', dashboard_view, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/login/'), name='logout'),
    path('register/', register_view, name='register'),

    # API modules
    path('api/users/', include('users.urls')),
    path('api/telegram/', include('telegram_accounts.urls')),
    path('api/', include('scheduled_posts.urls')),

    # Swagger / Redoc
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
    path('swagger.json', schema_view.without_ui(cache_timeout=0), name='schema-json'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)