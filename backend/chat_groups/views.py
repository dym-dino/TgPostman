"""
Chat group views
Views for managing chat groups via web and API.
"""

# --------------------------------------------------------------------------------

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render, redirect
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from telegram_accounts.models import TelegramChat
from .forms import ChatGroupForm, ChatGroupMemberForm
from .models import ChatGroup, ChatGroupMember
from .serializers import ChatGroupSerializer, ChatGroupMemberSerializer

# --------------------------------------------------------------------------------

@method_decorator(login_required, name='dispatch')
class ChatGroupListCreateView(View):
    def get(self, request):
        q = request.GET.get('q', '')
        groups_qs = ChatGroup.objects.filter(user=request.user)
        if q:
            groups_qs = groups_qs.filter(name__icontains=q)

        paginator = Paginator(groups_qs.order_by('-created_at'), 10)
        page = request.GET.get('page', 1)
        try:
            groups = paginator.page(page)
        except PageNotAnInteger:
            groups = paginator.page(1)
        except EmptyPage:
            groups = paginator.page(paginator.num_pages)

        form = ChatGroupForm()
        return render(request, 'chat_groups/group_list.html', {
            'groups': groups,
            'form': form,
            'q': q,
        })

    def post(self, request):
        form = ChatGroupForm(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.user = request.user
            group.save()
            return redirect('chat_groups:group_list')

        groups = Paginator(
            ChatGroup.objects.filter(user=request.user).order_by('-created_at'), 10
        ).page(1)
        return render(request, 'chat_groups/group_list.html', {
            'groups': groups,
            'form': form,
            'q': '',
        })

# --------------------------------------------------------------------------------

class ChatGroupDeleteView(View):
    def post(self, request, pk):
        group = get_object_or_404(ChatGroup, pk=pk, user=request.user)
        group.delete()
        return redirect('chat_groups:group_list')

# --------------------------------------------------------------------------------

@method_decorator(login_required, name='dispatch')
class ChatGroupMemberManageView(View):
    def get(self, request, pk):
        group = get_object_or_404(ChatGroup, pk=pk, user=request.user)
        q = request.GET.get('q', '')
        items = []

        for member in group.members.all():
            chat = TelegramChat.objects.filter(
                chat_id=member.chat_id, user=request.user
            ).first()
            title = chat.title if chat else ''
            if not q or q.lower() in title.lower():
                items.append({'member': member, 'chat': chat})

        paginator = Paginator(items, 10)
        page = request.GET.get('page', 1)
        try:
            members = paginator.page(page)
        except PageNotAnInteger:
            members = paginator.page(1)
        except EmptyPage:
            members = paginator.page(paginator.num_pages)

        form = ChatGroupMemberForm(user=request.user, group=group)
        return render(request, 'chat_groups/member_list.html', {
            'group': group,
            'members': members,
            'form': form,
            'q': q,
        })

    def post(self, request, pk):
        group = get_object_or_404(ChatGroup, pk=pk, user=request.user)
        if 'add_member' in request.POST:
            form = ChatGroupMemberForm(request.POST, user=request.user, group=group)
            if form.is_valid():
                member = form.save(commit=False)
                member.group = group
                member.save()
                return redirect('chat_groups:member_list', pk=pk)
        elif 'delete_member' in request.POST:
            member_id = request.POST.get('member_id')
            member = get_object_or_404(ChatGroupMember, pk=member_id, group=group)
            member.delete()
            return redirect('chat_groups:member_list', pk=pk)

        return self.get(request, pk)

# --------------------------------------------------------------------------------

class ChatGroupViewSet(viewsets.ModelViewSet):
    serializer_class = ChatGroupSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return ChatGroup.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def add_member(self, request, pk=None):
        group = get_object_or_404(ChatGroup, pk=pk, user=request.user)
        serializer = ChatGroupMemberSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(group=group)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['delete'], url_path='remove-member/(?P<member_id>[^/.]+)')
    def remove_member(self, request, pk=None, member_id=None):
        group = get_object_or_404(ChatGroup, pk=pk, user=request.user)
        member = group.members.filter(id=member_id).first()
        if not member:
            return Response(status=status.HTTP_404_NOT_FOUND)
        member.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
