from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import TelegramUser, NotificationLog
from .serializers import TelegramUserSerializer, NotificationLogSerializer
from .services.telegram_service import TelegramService
from common.permissions import IsAuthenticatedAndActive  # Added
from .utils.helpers import format_message

class TelegramUserListCreateView(APIView):
    """List and create Telegram users."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        users = TelegramUser.objects.filter(user=request.user)
        serializer = TelegramUserSerializer(users, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TelegramUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TelegramUserDetailView(APIView):
    """Retrieve, update, delete Telegram user."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        user = get_object_or_404(TelegramUser, pk=pk, user=request.user)
        serializer = TelegramUserSerializer(user)
        return Response(serializer.data)

    def put(self, request, pk):
        user = get_object_or_404(TelegramUser, pk=pk, user=request.user)
        serializer = TelegramUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        user = get_object_or_404(TelegramUser, pk=pk, user=request.user)
        user.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class NotificationLogListView(APIView):
    """List notification logs."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        logs = NotificationLog.objects.filter(user=request.user)
        serializer = NotificationLogSerializer(logs, many=True)
        return Response(serializer.data)

class SendNotificationView(APIView):
    """Send a notification."""
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request):
        message_type = request.data.get('message_type')
        channel = request.data.get('channel', 'telegram')
        telegram_user = get_object_or_404(TelegramUser, user=request.user)
        service = TelegramService()
        try:
            service.send_message(telegram_user.chat_id, format_message(message_type))
            NotificationLog.objects.create(user=request.user, message_type=message_type, channel=channel)
            return Response({"message": "Notification sent"})
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
