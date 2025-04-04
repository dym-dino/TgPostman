"""
Scheduled task

This file defines a Celery task to send a scheduled post and update its status accordingly.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from celery import shared_task

from .models import ScheduledPost
from .post_sender import send_post

# --------------------------------------------------------------------------------
# CELERY TASK

@shared_task
def send_scheduled_post(post_id: int) -> None:
    """
    Celery task to send a ScheduledPost by ID.
    Updates the status based on the result of the operation.

    :param post_id: ID of the ScheduledPost to be sent
    """
    try:
        post = ScheduledPost.objects.get(id=post_id)
        send_post(post)
        post.status = "sent"
    except Exception as e:
        post.status = "failed"
        post.error_message = str(e)
    finally:
        post.save()
