"""
URL configuration for tgpostman project.

This file contains the URL patterns for the web interface, API modules, and documentation.
"""

# --------------------------------------------------------------------------------
# IMPORTS

import base64
import os

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.urls import path, include, re_path
from django.views.generic import RedirectView
from django.views.static import serve
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

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
# BASIC AUTH DECORATOR

def swagger_basic_auth(view_func):
    def wrapper(request, *args, **kwargs):
        try:
            auth_header = request.META.get('HTTP_AUTHORIZATION')
            if auth_header is None or not auth_header.startswith('Basic '):
                return HttpResponse('Unauthorized', status=401, headers={'WWW-Authenticate': 'Basic'})

            encoded_credentials = auth_header.split(' ')[1]
            decoded_credentials = base64.b64decode(encoded_credentials).decode('utf-8')
            username, password = decoded_credentials.split(':', 1)

            if username == settings.ADMIN_SWAGGER_LOGIN and password == settings.ADMIN_SWAGGER_PASSWORD:
                return view_func(request, *args, **kwargs)
        except Exception:
            pass

        return HttpResponse('Unauthorized', status=401, headers={'WWW-Authenticate': 'Basic'})

    return wrapper


# --------------------------------------------------------------------------------
# DOCUMENTATION VIEWS (PROTECTED)

@swagger_basic_auth
def protected_swagger_ui(request):
    return schema_view.with_ui('swagger', cache_timeout=0)(request)


@swagger_basic_auth
def protected_redoc_ui(request):
    return schema_view.with_ui('redoc', cache_timeout=0)(request)


@swagger_basic_auth
def protected_schema_json(request):
    return schema_view.without_ui(cache_timeout=0)(request)


@swagger_basic_auth
def code_docs(request, path):
    """
    Serves documentation files from a directory (Sphinx HTML).

    If the requested file does not exist or is a directory, redirects to index.html.
    """
    docs_root = os.path.join(settings.BASE_DIR, 'docs/html')
    file_path = os.path.join(docs_root, path)
    if not os.path.exists(file_path) or os.path.isdir(file_path):
        return HttpResponseRedirect('/code_docs/index.html')

    return serve(request, path, document_root=docs_root)


# --------------------------------------------------------------------------------
# ERROR VIEWS

def errors_handling(request, exception=None) -> HttpResponse:
    """Custom error page"""
    return render(request, 'errors/index.html')


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

    # Swagger / Redoc (with basic auth)
    path('swagger/', protected_swagger_ui, name='schema-swagger-ui'),
    path('redoc/', protected_redoc_ui, name='schema-redoc'),
    path('swagger.json', protected_schema_json, name='schema-json'),

    # Sphinx docs (with basic auth)
    path('code_docs', RedirectView.as_view(url='/code_docs/index.html', permanent=False)),
    re_path(r'^code_docs/(?P<path>.*)$', code_docs, name='code_docs'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Error handlers
handler404 = errors_handling
handler403 = errors_handling
handler500 = errors_handling
