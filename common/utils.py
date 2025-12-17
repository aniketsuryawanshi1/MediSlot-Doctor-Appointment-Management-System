from datetime import datetime, timedelta
from django.utils import timezone


def get_current_datetime():
    """Get the current datetime in UTC."""
    return timezone.now()


def add_days_to_date(date, days):
    """Add a number of days to a given date."""
    return date + timedelta(days=days)


def format_datetime_for_display(dt):
    """Format datetime for user-friendly display (e.g., 'Dec 16, 2025 10:00 AM')."""
    return dt.strftime("%b %d, %Y %I:%M %p")


def is_past_datetime(dt):
    """Check if a datetime is in the past."""
    return dt < get_current_datetime()


def calculate_age(birth_date):
    """Calculate age from birth date."""
    today = get_current_datetime().date()
    return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))