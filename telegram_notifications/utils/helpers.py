from .constants import MESSAGE_TYPES

def format_message(message_type):
    """Format message based on type."""
    if message_type not in MESSAGE_TYPES:
        return "Invalid message type"
    templates = {
        'booking': "Your appointment has been booked successfully.",
        'reminder': "Reminder: You have an upcoming appointment.",
        'cancellation': "Your appointment has been canceled.",
        'reschedule': "Your appointment has been rescheduled."
    }
    return templates.get(message_type, "Notification")