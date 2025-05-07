"""
Telegram chat views

This file contains views for managing Telegram chats, including listing, adding, deleting, and API-based interactions.
"""

# --------------------------------------------------------------------------------
# IMPORTS

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from tgpostman.settings import BOT_USERNAME
from .forms import AddChatForm, TelegramChatForm
from .models import TelegramChat
from .serializers import TelegramChatSerializer
from .telegram_api import get_chat_info


# --------------------------------------------------------------------------------
# VIEWS

@method_decorator(login_required, name='dispatch')
class TelegramChatListCreateView(View):
    """
    View for listing and creating Telegram chats with search & pagination.
    """

    def get(self, request):
        """
        Handle GET request to display the form and user's Telegram chats.
        Supports optional search query and pagination.
        """
        form = TelegramChatForm(user=request.user)
        q = request.GET.get('q', '')
        chats_qs = TelegramChat.objects.filter(user=request.user)
        if q:
            chats_qs = chats_qs.filter(title__icontains=q)

        # Pagination
        page = request.GET.get('page', 1)
        paginator = Paginator(chats_qs.order_by('title'), 10)  # 10 per page
        try:
            chats = paginator.page(page)
        except PageNotAnInteger:
            chats = paginator.page(1)
        except EmptyPage:
            chats = paginator.page(paginator.num_pages)

        context = {
            'form': form,
            'chats': chats,
            'q': q,
            'bot_username': BOT_USERNAME,
        }
        return render(request, 'telegram_accounts/manage.html', context)

    def post(self, request):
        """
        Handle POST request to create a new Telegram chat.
        After saving, redirect to first page (no query args).
        """
        form = TelegramChatForm(request.POST, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('manage_telegram_chats')

        # If form invalid, re-display page 1 of results without search
        chats_qs = TelegramChat.objects.filter(user=request.user).order_by('title')
        paginator = Paginator(chats_qs, 10)
        chats = paginator.page(1)
        return render(request, 'telegram_accounts/manage.html',
                      {'form': form, 'chats': chats, 'q': '', 'bot_username': BOT_USERNAME, })


@method_decorator(login_required, name='dispatch')
class TelegramChatDeleteView(View):
    """
    View for deleting a Telegram chat.
    """

    def post(self, request, pk):
        """
        Handle POST request to delete a chat by its primary key (pk).
        """
        chat = get_object_or_404(TelegramChat, pk=pk, user=request.user)
        chat.delete()
        return redirect('manage_telegram_chats')


@login_required
def add_chat_view(request):
    """
    View for adding a new Telegram chat.
    """
    if request.method == "POST":
        form = AddChatForm(request.POST)
        if form.is_valid():
            chat_id = form.cleaned_data["chat_id"]
            try:
                chat_info = get_chat_info(chat_id)
                chat, created = TelegramChat.objects.get_or_create(
                    user=request.user,
                    chat_id=chat_id,
                    defaults={
                        "title": chat_info["title"],
                        "can_post": chat_info["can_post"],
                        "chat_type": chat_info["chat_type"],
                        "url": chat_info["url"],
                    }
                )
                if created:
                    messages.success(request, f"Чат '{chat.title}' успешно добавлен!")
                else:
                    messages.info(request, f"Чат уже существует: {chat.title}")
                return redirect("dashboard")
            except Exception as e:
                messages.error(request, f"Ошибка: {e}")
    else:
        form = AddChatForm()
    return render(request, "telegram_accounts/add_chat.html", {"form": form})


class TelegramChatViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Telegram chats via API.
    """

    queryset = TelegramChat.objects.all()
    serializer_class = TelegramChatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        """
        Return the queryset of Telegram chats for the current user.
        """
        return TelegramChat.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """
        Override the default create method to add chat info during creation.
        """
        chat_info = get_chat_info(self.request.data["chat_id"])
        serializer.save(
            user=self.request.user,
            title=chat_info["title"],
            can_post=chat_info["can_post"],
            chat_type=chat_info["chat_type"],
            url=chat_info["url"],
        )

    @action(detail=False, methods=['get'], url_path='my')
    def list_my_chats(self, request):
        """
        List chats that belong to the authenticated user.
        """
        chats = self.get_queryset()
        serializer = self.get_serializer(chats, many=True)
        return Response(serializer.data)
