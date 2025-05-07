"""
Scheduled task
This file defines a Celery task to send a scheduled post and update its status accordingly.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from celery import shared_task
from django.db import transaction

from .models import ScheduledPost
from .post_sender import send_post

# --------------------------------------------------------------------------------
# CELERY TASK


@shared_task
def send_scheduled_post(post_id: int) -> None:
    """
    Celery task to send a scheduled post and update its status.

    Args:
        post_id (int): ID of the ScheduledPost to send.

    Returns:
        None
    """
    post = None
    try:
        post = ScheduledPost.objects.get(id=post_id)
        send_post(post)
        post.status = 'sent'
        post.error_message = ''
    except ScheduledPost.DoesNotExist:
        return
    except Exception as e:
        if post:
            post.status = 'failed'
            post.error_message = str(e)
    finally:
        if post:
            with transaction.atomic():
                post.save()
