from ..models import Appointment, WaitingList
from ..serializers import AppointmentSerializer
from doctors.models import DoctorProfile, Schedule
from common.exceptions import AppointmentConflictError
from common.utils import get_current_datetime
from ..utils.validators import validate_appointment
from ..utils.constants import CANCELLATION_POLICY_HOURS
from ..utils.helpers import is_past_datetime
from datetime import timedelta
from django.utils import timezone

class AppointmentFactory:
    """Factory for creating appointments (GOF: Factory Pattern)."""
    @staticmethod
    def create_appointment(patient, doctor, data):
        validate_appointment(data)
        appointment = Appointment.objects.create(patient=patient, doctor=doctor, **data)
        return appointment

class BookingService:
    """Service for booking, canceling, rescheduling."""
    def book_appointment(self, patient, data):
        doctor_id = data.get('doctor')
        doctor = DoctorProfile.objects.get(id=doctor_id)
        # Check availability (integrate with doctor's schedule service)
        from doctors.services.schedule_service import ScheduleService
        service = ScheduleService()
        if not service.check_availability(doctor, data['appointment_date'], data['start_time'], data['end_time']):
            # Add to waiting list
            WaitingList.objects.create(patient=patient, doctor=doctor, requested_date=data['appointment_date'], requested_time=data['start_time'])
            raise ValueError("Slot unavailable; added to waiting list.")
        return AppointmentFactory.create_appointment(patient, doctor, data)

    def cancel_appointment(self, appointment):
        if is_past_datetime(appointment.appointment_date) or (timezone.now() + timedelta(hours=CANCELLATION_POLICY_HOURS)) > timezone.datetime.combine(appointment.appointment_date, appointment.start_time):
            raise ValueError("Cannot cancel within policy hours.")
        appointment.status = 'canceled'
        appointment.save()
        # Notify (integrate with notification service)

    def reschedule_appointment(self, appointment, data):
        new_date = data.get('appointment_date')
        new_start = data.get('start_time')
        new_end = data.get('end_time')
        from doctors.services.schedule_service import ScheduleService
        service = ScheduleService()
        if not service.check_availability(appointment.doctor, new_date, new_start, new_end):
            raise AppointmentConflictError("New slot unavailable.")
        appointment.appointment_date = new_date
        appointment.start_time = new_start
        appointment.end_time = new_end
        appointment.status = 'rescheduled'
        appointment.save()
        return appointment