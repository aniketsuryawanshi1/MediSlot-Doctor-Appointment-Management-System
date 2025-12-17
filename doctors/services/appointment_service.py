from patients.models import Appointment
from patients.serializers import AppointmentSerializer


class AppointmentService:
    """Service for doctor to view/manage appointments."""
    def get_appointments(self, doctor, status=None):
        """Retrieve doctor's appointments."""
        queryset = Appointment.objects.filter(doctor=doctor)
        if status:
            queryset = queryset.filter(status=status)
        return queryset.order_by('appointment_date')

    def confirm_appointment(self, appointment):
        """Confirm an appointment."""
        if appointment.status == 'booked':
            appointment.status = 'confirmed'
            appointment.save()
            # Trigger notification (integrate with telegram_notifications later)
            return appointment
        raise ValueError("Cannot confirm appointment.")

    def view_upcoming(self, doctor):
        """Get upcoming appointments."""
        from django.utils import timezone
        return self.get_appointments(doctor).filter(appointment_date__gte=timezone.now().date())