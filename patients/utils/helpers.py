from datetime import datetime, timedelta
from django.utils import timezone  # Added

def is_past_datetime(dt):
    """Check if datetime is past."""
    return dt < timezone.now()

def add_hours_to_datetime(dt, hours):
    """Add hours to datetime."""
    return dt + timedelta(hours=hours)

def format_appointment_display(appointment):
    """Format appointment for display."""
    return f"{appointment.appointment_date} {appointment.start_time} - {appointment.end_time}"