from datetime import datetime, timedelta
from django.utils import timezone


def add_hours_to_time(base_time, hours):
    """Add hours to a time object."""
    dt = datetime.combine(datetime.today(), base_time) + timedelta(hours=hours)
    return dt.time()


def is_time_within_range(check_time, start, end):
    """Check if time is within range."""
    return start <= check_time <= end


def format_slot_display(start, end):
    """Format time slot for display."""
    return f"{start.strftime('%I:%M %p')} - {end.strftime('%I:%M %p')}"


def calculate_age_from_dob(dob):
    """Calculate age from date of birth."""
    today = timezone.now().date()
    return today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))