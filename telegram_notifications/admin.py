from django.contrib import admin
from .models import TelegramUser, NotificationLog

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ['user', 'chat_id', 'is_active']
    search_fields = ['user__username']

@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'message_type', 'channel', 'status']
    list_filter = ['channel', 'status']
