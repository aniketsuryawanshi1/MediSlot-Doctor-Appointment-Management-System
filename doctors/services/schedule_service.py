from ..models import Schedule
from ..serializers import ScheduleSerializer
from common.exceptions import InvalidScheduleError
from patients.models import Appointment
from datetime import datetime, time, timedelta
from ..utils.validators import validate_schedule  # Added
from ..utils.helpers import add_hours_to_time  # Added for slot calc
from common.utils import get_current_datetime  # Added


class ScheduleFactory:
    """Factory for creating Schedule instances (GOF: Factory Pattern)."""
    @staticmethod
    def create_schedule(doctor, day_of_week, start_time, end_time, **kwargs):
        if Schedule.objects.filter(doctor=doctor, day_of_week=day_of_week).exists():
            raise ValueError("Schedule already exists for this day.")
        schedule = Schedule.objects.create(
            doctor=doctor, day_of_week=day_of_week, start_time=start_time, end_time=end_time, **kwargs
        )
        return schedule


class AvailabilityStrategy:
    """Strategy for checking availability (GOF: Strategy Pattern)."""
    def check_availability(self, doctor, date, start_time, end_time):
        raise NotImplementedError


class WeeklyAvailabilityStrategy(AvailabilityStrategy):
    """Check against weekly schedule."""
    def check_availability(self, doctor, date, start_time, end_time):
        day = date.strftime('%A').lower()
        schedule = Schedule.objects.filter(doctor=doctor, day_of_week=day, is_available=True).first()
        if not schedule:
            return False
        # Check within hours, excluding breaks
        if not (schedule.start_time <= start_time < schedule.end_time and
                schedule.start_time < end_time <= schedule.end_time):
            return False
        if schedule.break_start and schedule.break_end:
            if (schedule.break_start <= start_time < schedule.break_end or
                schedule.break_start < end_time <= schedule.break_end):
                return False
        return True


class ScheduleService:
    """Service for schedule operations."""
    def __init__(self):
        self.strategy = WeeklyAvailabilityStrategy()  # Default strategy

    def get_schedules(self, doctor):
        """Retrieve doctor's schedules."""
        return Schedule.objects.filter(doctor=doctor)

    def create_schedule(self, doctor, data):
        """Create a new schedule."""
        validate_schedule(data)  # Use validator
        serializer = ScheduleSerializer(data=data)
        if serializer.is_valid():
            return serializer.save(doctor=doctor)
        raise InvalidScheduleError(serializer.errors)

    def update_schedule(self, schedule, data):
        """Update schedule."""
        serializer = ScheduleSerializer(schedule, data=data, partial=True)
        if serializer.is_valid():
            return serializer.save()
        raise InvalidScheduleError(serializer.errors)

    def check_availability(self, doctor, date, start_time, end_time):
        """Check if slot is available using strategy."""
        if not self.strategy.check_availability(doctor, date, start_time, end_time):
            return False
        # Check for existing appointments
        if Appointment.objects.filter(
            doctor=doctor, appointment_date=date,
            start_time__lt=end_time, end_time__gt=start_time, status__in=['booked', 'confirmed']
        ).exists():
            return False
        return True

    def get_available_slots(self, doctor, date):
        """Get available slots for a date."""
        day = date.strftime('%A').lower()
        schedule = Schedule.objects.filter(doctor=doctor, day_of_week=day, is_available=True).first()
        if not schedule:
            return []
        slots = []
        current = schedule.start_time
        while current < schedule.end_time:
            end_slot = add_hours_to_time(date, current, 1)  # Use helper to add hour
            if end_slot <= schedule.end_time and self.check_availability(doctor, date, current, end_slot):
                slots.append((current, end_slot))
            current = end_slot
        return slots