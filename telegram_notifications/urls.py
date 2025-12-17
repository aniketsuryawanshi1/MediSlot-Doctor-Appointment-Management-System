from django.urls import path
from .views import (
    TelegramUserListCreateView, TelegramUserDetailView,
    NotificationLogListView, SendNotificationView
)

urlpatterns = [
    # Telegram User Endpoints
    path('users/', TelegramUserListCreateView.as_view(), name='telegram-user-list-create'),
    path('users/<uuid:pk>/', TelegramUserDetailView.as_view(), name='telegram-user-detail'),

    # Notification Endpoints
    path('logs/', NotificationLogListView.as_view(), name='notification-log-list'),
    path('send/', SendNotificationView.as_view(), name='send-notification'),
]