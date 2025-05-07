"""
URL patterns
This file contains the URL patterns for the scheduled posts functionality.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.urls import path

from .views import (
    ScheduledPostListCreateView,
    create_post_view,
    my_posts_view,
    send_post_now,
    cancel_post,
    download_attachment
)

# --------------------------------------------------------------------------------
# URLS

urlpatterns = [
    path('posts/', ScheduledPostListCreateView.as_view(), name='posts'),
    path('create-post/', create_post_view, name='create_post'),
    path('my-posts/', my_posts_view, name='my_posts'),
    path('send-now/<int:post_id>/', send_post_now, name='send_post_now'),
    path('cancel-post/<int:post_id>/', cancel_post, name='cancel_post'),
    path(
        'attachments/<int:attachment_id>/download/',
        download_attachment,
        name='download_attachment'
    ),
]
