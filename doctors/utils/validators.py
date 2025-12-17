from django.core.exceptions import ValidationError
from .constants import DAYS_OF_WEEK, SPECIALTIES
from .helpers import is_time_within_range

class ValidationStrategy:
    """Base strategy for validations (GOF: Strategy Pattern)."""
    def validate(self, data):
        raise NotImplementedError

class ScheduleValidationStrategy(ValidationStrategy):
    """Validate schedule data."""
    def validate(self, data):
        day = data.get('day_of_week')
        start = data.get('start_time')
        end = data.get('end_time')
        break_start = data.get('break_start')
        break_end = data.get('break_end')

        if day not in DAYS_OF_WEEK:
            raise ValidationError("Invalid day of week.")
        if start and end and start >= end:
            raise ValidationError("Start time must be before end time.")
        if break_start and break_end:
            if not is_time_within_range(break_start, start, end) or not is_time_within_range(break_end, start, end):
                raise ValidationError("Break times must be within working hours.")

class ProfileValidationStrategy(ValidationStrategy):
    """Validate doctor profile data."""
    def validate(self, data):
        specialty = data.get('specialty')
        if specialty and specialty not in SPECIALTIES:
            raise ValidationError("Invalid specialty.")

def validate_schedule(data):
    """Helper to run schedule validation."""
    strategy = ScheduleValidationStrategy()
    strategy.validate(data)

def validate_profile(data):
    """Helper to run profile validation."""
    strategy = ProfileValidationStrategy()
    strategy.validate(data)