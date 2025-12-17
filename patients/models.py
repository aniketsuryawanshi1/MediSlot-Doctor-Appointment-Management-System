from django.db import models
from django.contrib.auth import get_user_model
from doctors.models import DoctorProfile
from common.mixins import TimestampMixin, SoftDeleteMixin

User = get_user_model()


class PatientProfile(TimestampMixin, SoftDeleteMixin):
    """Model for patient profiles, linked to CustomUser (GOF: Composition via mixins)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    date_of_birth = models.DateField(help_text="Patient's date of birth")
    gender = models.CharField(
        max_length=10,
        choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
        help_text="Gender"
    )
    emergency_contact = models.CharField(max_length=100, blank=True, help_text="Emergency contact name")
    emergency_phone = models.CharField(max_length=15, blank=True, help_text="Emergency contact phone")
    medical_history = models.TextField(blank=True, help_text="Brief medical history")

    def __str__(self):
        return f"{self.user.get_full_name()} - Patient"


class Appointment(TimestampMixin, SoftDeleteMixin):
    """Model for appointments, linking patients and doctors (GOF: Factory pattern implied in creation logic)."""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='appointments')
    appointment_date = models.DateField(help_text="Appointment date")
    start_time = models.TimeField(help_text="Start time")
    end_time = models.TimeField(help_text="End time")
    service_type = models.CharField(
        max_length=50,
        choices=[('consultation', 'Consultation'), ('lab', 'Lab'), ('follow_up', 'Follow-up')],
        help_text="Type of service"
    )
    status = models.CharField(
        max_length=20,
        choices=[
            ('booked', 'Booked'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled'),
            ('completed', 'Completed'), ('rescheduled', 'Rescheduled')
        ],
        default='booked',
        help_text="Appointment status"
    )
    notes = models.TextField(blank=True, help_text="Additional notes or reason")
    appointment_id = models.CharField(max_length=20, unique=True, editable=False, help_text="Unique appointment ID")

    class Meta:
        unique_together = ('doctor', 'appointment_date', 'start_time')

    def save(self, *args, **kwargs):
        if not self.appointment_id:
            self.appointment_id = f"APT-{self.pk or 'NEW'}-{self.appointment_date.strftime('%Y%m%d')}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Appointment {self.appointment_id} - {self.patient} with {self.doctor}"


class WaitingList(TimestampMixin):
    """Model for waiting lists when slots are full (GOF: Observer pattern for notifications)."""
    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='waiting_list')
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='waiting_list')
    requested_date = models.DateField(help_text="Preferred date")
    requested_time = models.TimeField(help_text="Preferred time")
    notes = models.TextField(blank=True, help_text="Additional notes")
    is_notified = models.BooleanField(default=False, help_text="Has the patient been notified of availability?")

    def __str__(self):
        return f"Waiting: {self.patient} for {self.doctor} on {self.requested_date}"
