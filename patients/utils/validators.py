from django.core.exceptions import ValidationError
from .constants import SERVICE_TYPES, GENDERS
from django.utils import timezone


class ValidationStrategy:
    """Base strategy for validations (GOF: Strategy Pattern)."""
    def validate(self, data):
        raise NotImplementedError


class AppointmentValidationStrategy(ValidationStrategy):
    """Validate appointment data."""
    def validate(self, data):
        date = data.get('appointment_date')
        service_type = data.get('service_type')
        
        if date:
            # FIXED: Convert date to datetime for comparison
            # Check if the date is in the past
            today = timezone.now().date()
            if date < today:
                raise ValidationError("Appointment date cannot be in the past.")
        
        if service_type and service_type not in SERVICE_TYPES:
            raise ValidationError("Invalid service type.")


class ProfileValidationStrategy(ValidationStrategy):
    """Validate patient profile data."""
    def validate(self, data):
        gender = data.get('gender')
        if gender and gender not in GENDERS:
            raise ValidationError("Invalid gender.")


def validate_appointment(data):
    """Helper to run appointment validation."""
    strategy = AppointmentValidationStrategy()
    strategy.validate(data)


def validate_profile(data):
    """Helper to run profile validation."""
    strategy = ProfileValidationStrategy()
    strategy.validate(data)