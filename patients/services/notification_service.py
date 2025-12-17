from ..models import Appointment
from telegram_notifications.models import NotificationLog
from common.utils import get_current_datetime
from ..utils.constants import REMINDER_HOURS_BEFORE
from datetime import timedelta  # FIXED: Added missing import
from django.utils import timezone  # FIXED: Added missing import


class NotificationStrategy:
    """Strategy for notification types (GOF: Strategy Pattern)."""
    def send(self, user, message_type, channel):
        raise NotImplementedError


class EmailNotificationStrategy(NotificationStrategy):
    """Send via email."""
    def send(self, user, message_type, channel):
        # Integrate with authentication utils
        from authentication.utils import send_email
        send_email("Appointment Update", f"Your {message_type} notification.", user.email)


class TelegramNotificationStrategy(NotificationStrategy):
    """Send via Telegram."""
    def send(self, user, message_type, channel):
        # Integrate with telegram service
        from telegram_notifications.services.telegram_service import TelegramService
        service = TelegramService()
        service.send_message(user.telegram_user.chat_id, f"Your {message_type} notification.")


class NotificationService:
    """Service for sending notifications (GOF: Observer for event triggers)."""
    def __init__(self):
        self.strategies = {
            'email': EmailNotificationStrategy(),
            'telegram': TelegramNotificationStrategy()
        }

    def send_notification(self, user, message_type, channel='email'):
        strategy = self.strategies.get(channel)
        if strategy:
            strategy.send(user, message_type, channel)
            NotificationLog.objects.create(user=user, message_type=message_type, channel=channel)

    def send_reminder(self, appointment):
        """Send reminder for upcoming appointment."""
        # FIXED: Proper datetime comparison
        appointment_datetime = timezone.datetime.combine(
            appointment.appointment_date, 
            appointment.start_time
        )
        # Make it timezone-aware
        appointment_datetime = timezone.make_aware(appointment_datetime)
        
        reminder_time = appointment_datetime - timedelta(hours=REMINDER_HOURS_BEFORE)
        
        if timezone.now() >= reminder_time:
            self.send_notification(appointment.patient.user, 'reminder')


# Added Observer for triggers
class NotificationObserver:
    """Observer pattern for notification triggers."""
    def __init__(self):
        self.service = NotificationService()
    
    def update(self, event, appointment):
        """
        Update method called when an event occurs.
        
        Args:
            event: Type of event (booking, cancellation, reschedule)
            appointment: The appointment object
        """
        if event == 'booking':
            self.service.send_notification(appointment.patient.user, 'booking')
        elif event == 'cancellation':
            self.service.send_notification(appointment.patient.user, 'cancellation')
        elif event == 'reschedule':
            self.service.send_notification(appointment.patient.user, 'reschedule')
        elif event == 'reminder':
            self.service.send_reminder(appointment)