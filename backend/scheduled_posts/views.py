"""
Scheduled post views
Views for creating, listing, sending, and cancelling scheduled posts.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from datetime import timedelta

from celery.result import AsyncResult
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from .forms import CreatePostForm
from .models import ScheduledPost, ScheduledPostAttachment
from .serializers import ScheduledPostSerializer
from .tasks import send_scheduled_post


# --------------------------------------------------------------------------------


class ScheduledPostListCreateView(generics.ListCreateAPIView):
    """
    API view for listing and creating scheduled posts.

    Returns:
        QuerySet of posts belonging to the authenticated user.
    """

    serializer_class = ScheduledPostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """
        Filter posts by the current authenticated user.

        Returns:
            QuerySet: Scheduled posts ordered by schedule time.
        """
        return ScheduledPost.objects.filter(
            user=self.request.user
        ).order_by('-schedule_time')


# --------------------------------------------------------------------------------


@login_required
def create_post_view(request):
    """
    Render post creation form and handle form submission.

    Args:
        request (HttpRequest): The incoming request.

    Returns:
        HttpResponse: Rendered HTML or redirect on success.
    """
    if request.method == 'POST':
        form = CreatePostForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            if form.cleaned_data['schedule_option'] == 'delay':
                delay = min(form.cleaned_data.get('delay_seconds'), 10)
                schedule_time = timezone.localtime(timezone.now()) + timedelta(seconds=delay)
            else:
                schedule_time = form.cleaned_data.get(
                    'schedule_time',
                    timezone.localtime(timezone.now()) + timedelta(seconds=10)
                )

            if schedule_time <= timezone.localtime(timezone.now()):
                form.add_error('schedule_time', 'Время отправки должно быть в будущем!')
                return render(request, 'posts/create_post.html', {'form': form})

            if not form.cleaned_data['targets'] and not form.cleaned_data['groups']:
                form.add_error(None, 'Вы должны выбрать хотя бы один чат или группу для отправки.')
                return render(request, 'posts/create_post.html', {'form': form})

            post = ScheduledPost.objects.create(
                user=request.user,
                content=form.cleaned_data['content'],
                html=form.cleaned_data['html'],
                schedule_time=schedule_time,
                button_text=form.cleaned_data.get('button_text'),
                button_url=form.cleaned_data.get('button_url')
            )
            post.targets.set(form.cleaned_data['targets'])
            post.groups.set(form.cleaned_data['groups'])

            for f in form.cleaned_data['files']:
                original_name = f.name.split('_', 1)[-1]
                ScheduledPostAttachment.objects.create(
                    post=post,
                    file=f,
                    original_name=original_name
                )

            task = send_scheduled_post.apply_async(args=[post.id], eta=post.schedule_time)
            post.celery_task_id = task.id
            post.save()

            messages.success(request, 'Пост успешно создан и будет отправлен!')
            return redirect('my_posts')
    else:
        form = CreatePostForm(user=request.user)

    return render(request, 'posts/create_post.html', {'form': form})


# --------------------------------------------------------------------------------


@login_required
def my_posts_view(request):
    """
    Display paginated list of user's posts with search.

    Args:
        request (HttpRequest): Request object.

    Returns:
        HttpResponse: Rendered list of posts.
    """
    q = request.GET.get('q', '')
    posts_qs = ScheduledPost.objects.filter(
        user=request.user
    ).prefetch_related('targets', 'groups').order_by('-created_at')

    if q:
        posts_qs = posts_qs.filter(content__icontains=q)

    paginator = Paginator(posts_qs, 10)
    page = request.GET.get('page', 1)
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    form = CreatePostForm(user=request.user)
    return render(request, 'posts/my_posts.html', {'posts': posts, 'q': q, 'form': form})


# --------------------------------------------------------------------------------


@login_required
def send_post_now(request, post_id):
    """
    Immediately send a pending scheduled post.

    Args:
        request (HttpRequest): The incoming request.
        post_id (int): ID of the post to send.

    Returns:
        HttpResponseRedirect: Redirect back to post list.
    """
    post = ScheduledPost.objects.get(id=post_id, user=request.user)
    if post.status == 'pending':
        task = send_scheduled_post.apply_async(args=[post.id], eta=timezone.now())
        post.celery_task_id = task.id
        post.save()
        messages.success(request, 'Пост отправлен немедленно!')
    else:
        messages.error(request, 'Пост уже был отправлен или не может быть отправлен.')

    return redirect('my_posts')


# --------------------------------------------------------------------------------


@login_required
def cancel_post(request, post_id):
    """
    Cancel a scheduled post if it hasn't been sent yet.

    Args:
        request (HttpRequest): The incoming request.
        post_id (int): ID of the post to cancel.

    Returns:
        HttpResponseRedirect: Redirect back to post list.
    """
    try:
        post = ScheduledPost.objects.get(id=post_id, user=request.user)
        if post.status == 'pending' and post.celery_task_id:
            result = AsyncResult(post.celery_task_id)
            if result.state == 'PENDING':
                result.revoke(terminate=True)
                post.status = 'failed'
                post.error_message = 'Пост был отменен пользователем.'
                post.save()
                messages.success(request, 'Пост был отменен!')
            else:
                messages.error(request, 'Невозможно отменить задачу, она уже была выполнена.')
        else:
            messages.error(request, 'Пост уже был отправлен или не может быть отменен.')
    except ScheduledPost.DoesNotExist:
        messages.error(request, 'Пост не найден.')

    return redirect('my_posts')


# --------------------------------------------------------------------------------


@login_required
def download_attachment(request, attachment_id):
    """
    Download an attachment file belonging to the current user.

    Args:
        request (HttpRequest): The incoming request.
        attachment_id (int): ID of the attachment to download.

    Returns:
        FileResponse: File stream response if found.
    """
    attachment = get_object_or_404(
        ScheduledPostAttachment,
        pk=attachment_id,
        post__user=request.user
    )
    try:
        return FileResponse(
            attachment.file.open('rb'),
            as_attachment=True,
            filename=attachment.original_name
        )
    except FileNotFoundError:
        raise Http404("Файл не найден")
