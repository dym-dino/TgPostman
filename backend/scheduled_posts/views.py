"""
Views for scheduled posts

This file contains views for listing, creating, and displaying scheduled posts.
"""
from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import CreatePostForm
from .models import ScheduledPost
from .serializers import ScheduledPostSerializer
from .tasks import send_scheduled_post


# --------------------------------------------------------------------------------
# IMPORTS


# --------------------------------------------------------------------------------
# VIEWS

class ScheduledPostListCreateView(generics.ListCreateAPIView):
    """
    View for listing and creating scheduled posts.
    Requires the user to be authenticated.
    """
    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Return the queryset of posts for the current user.
        """
        return ScheduledPost.objects.filter(user=self.request.user)


@login_required
def create_post_view(request):
    """
    View for creating a new scheduled post.
    """
    if request.method == "POST":
        form = CreatePostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            delay = form.cleaned_data["delay_seconds"]
            schedule_time = form.cleaned_data["schedule_time"]
            if not schedule_time:  # If no specific time is provided, use delay
                schedule_time = timezone.now() + timezone.timedelta(seconds=delay)
            elif schedule_time < timezone.now():
                form.add_error('schedule_time', 'Время отправки должно быть в будущем!')
                return render(request, "posts/create_post.html", {"form": form})

            post = ScheduledPost.objects.create(
                user=request.user,
                content=form.cleaned_data["content"],
                html=form.cleaned_data["html"],
                file=form.cleaned_data.get("file"),
                schedule_time=schedule_time,
            )
            post.targets.set(form.cleaned_data["targets"])

            task = send_scheduled_post.apply_async(args=[post.id], eta=post.schedule_time)
            post.celery_task_id = task.id
            post.save()

            messages.success(request, "Пост успешно создан и будет отправлен!")
            return redirect("dashboard")
    else:
        form = CreatePostForm(user=request.user)
    return render(request, "posts/create_post.html", {"form": form})


@login_required
def my_posts_view(request):
    """
    View for displaying all posts created by the current user.
    """
    posts = ScheduledPost.objects.filter(user=request.user).prefetch_related("targets").order_by("-created_at")
    return render(request, "posts/my_posts.html", {"posts": posts})


@login_required
def send_post_now(request, post_id):
    """
    View to manually send a scheduled post that is still pending.
    """
    post = ScheduledPost.objects.get(id=post_id, user=request.user)
    if post.status == 'pending':
        task_id = post.celery_task_id
        if task_id:
            result = AsyncResult(task_id)
            if result.state == 'PENDING':
                result.revoke(terminate=True)

        task = send_scheduled_post.apply_async(args=[post.id], eta=timezone.now())
        post.status = 'sent'
        post.celery_task_id = task.id
        post.save()
        messages.success(request, "Пост отправлен немедленно!")
    else:
        messages.error(request, "Пост уже был отправлен или не может быть отправлен.")
    return redirect("my_posts")


@login_required
def cancel_post(request, post_id):
    """
    View to cancel a scheduled post.
    """
    try:
        post = ScheduledPost.objects.get(id=post_id, user=request.user)

        if post.status == 'pending':
            task_id = post.celery_task_id
            if task_id:
                result = AsyncResult(task_id)
                if result.state == 'PENDING':
                    result.revoke(terminate=True)
                    post.status = 'failed'
                    post.error_message = 'Пост был отменен пользователем.'
                    post.save()
                    messages.success(request, "Пост был отменен!")
                else:
                    messages.error(request, "Невозможно отменить задачу, она уже была выполнена.")
            else:
                messages.error(request, "Задача не найдена.")
        else:
            messages.error(request, "Пост уже был отправлен или не может быть отменен.")

    except ScheduledPost.DoesNotExist:
        messages.error(request, "Пост не найден.")

    return redirect("my_posts")