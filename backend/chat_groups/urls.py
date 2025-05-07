"""
Chat group URLs
URL configuration for chat group views and API endpoints.
"""

# --------------------------------------------------------------------------------

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    ChatGroupListCreateView,
    ChatGroupDeleteView,
    ChatGroupMemberManageView,
    ChatGroupViewSet,
)

# --------------------------------------------------------------------------------

app_name = 'chat_groups'

router = DefaultRouter()
router.register(r'api/groups', ChatGroupViewSet, basename='chatgroup')

# --------------------------------------------------------------------------------

urlpatterns = [
    path('', ChatGroupListCreateView.as_view(), name='group_list'),
    path('delete/<int:pk>/', ChatGroupDeleteView.as_view(), name='group_delete'),
    path('<int:pk>/members/', ChatGroupMemberManageView.as_view(), name='member_list'),

    path('', include(router.urls)),
]
