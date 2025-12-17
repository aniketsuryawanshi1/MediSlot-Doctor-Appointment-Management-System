from rest_framework import serializers
from .models import TelegramUser, NotificationLog


class TelegramUserSerializer(serializers.ModelSerializer):
    """Serializer for linking users to Telegram."""
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = TelegramUser
        fields = ['id', 'user', 'chat_id', 'username', 'is_active', 'user_full_name', 'created_at']
        read_only_fields = ['id', 'created_at']


class NotificationLogSerializer(serializers.ModelSerializer):
    """Serializer for notification logs."""
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = NotificationLog
        fields = [
            'id', 'user', 'message_type', 'channel', 'sent_at', 'status',
            'error_message', 'user_full_name'
        ]
        read_only_fields = ['id', 'sent_at']