from django.db import models
from django.contrib.auth import get_user_model
from common.mixins import TimestampMixin  # Added

User = get_user_model()


class TelegramUser(TimestampMixin):
    """Model for linking users to Telegram chat IDs (GOF: Singleton implied for bot instance)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='telegram_user')
    chat_id = models.CharField(max_length=50, unique=True, help_text="Telegram chat ID")
    username = models.CharField(max_length=100, blank=True, help_text="Telegram username")
    is_active = models.BooleanField(default=True, help_text="Is the Telegram link active?")

    def __str__(self):
        return f"{self.user} - Telegram: {self.chat_id}"


class NotificationLog(TimestampMixin):
    """Model for logging sent notifications (GOF: Observer for event tracking)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notification_logs')
    message_type = models.CharField(
        max_length=20,
        choices=[
            ('booking', 'Booking Confirmation'), ('reminder', 'Reminder'),
            ('cancellation', 'Cancellation'), ('reschedule', 'Reschedule')
        ],
        help_text="Type of notification"
    )
    channel = models.CharField(
        max_length=10,
        choices=[('email', 'Email'), ('telegram', 'Telegram')],
        help_text="Notification channel"
    )
    sent_at = models.DateTimeField(auto_now_add=True, help_text="When the notification was sent")
    status = models.CharField(
        max_length=10,
        choices=[('sent', 'Sent'), ('failed', 'Failed')],
        default='sent',
        help_text="Delivery status"
    )
    error_message = models.TextField(blank=True, help_text="Error details if failed")

    def __str__(self):
        return f"{self.message_type} to {self.user} via {self.channel} - {self.status}"
