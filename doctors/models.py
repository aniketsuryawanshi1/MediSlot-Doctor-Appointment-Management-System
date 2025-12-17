from django.db import models
from django.contrib.auth import get_user_model
from common.mixins import TimestampMixin, SoftDeleteMixin  # Added

User = get_user_model()


class DoctorProfile(TimestampMixin, SoftDeleteMixin):
    """Model for doctor profiles, linked to CustomUser (GOF: Composition via mixins)."""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='doctor_profile')
    specialty = models.CharField(max_length=100, help_text="Doctor's specialty (e.g., Cardiology)")
    license_number = models.CharField(max_length=50, unique=True, help_text="Medical license number")
    experience_years = models.PositiveIntegerField(default=0, help_text="Years of experience")
    contact_phone = models.CharField(max_length=15, blank=True, help_text="Contact phone number")
    bio = models.TextField(blank=True, help_text="Short biography")

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.specialty}"


class Schedule(TimestampMixin, SoftDeleteMixin):
    """Model for doctor schedules, supporting weekly availability (GOF: Strategy for time slot logic)."""
    doctor = models.ForeignKey(DoctorProfile, on_delete=models.CASCADE, related_name='schedules')
    day_of_week = models.CharField(
        max_length=10,
        choices=[
            ('monday', 'Monday'), ('tuesday', 'Tuesday'), ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'), ('friday', 'Friday'), ('saturday', 'Saturday'), ('sunday', 'Sunday')
        ],
        help_text="Day of the week"
    )
    start_time = models.TimeField(help_text="Start time (e.g., 09:00)")
    end_time = models.TimeField(help_text="End time (e.g., 17:00)")
    break_start = models.TimeField(null=True, blank=True, help_text="Break start time")
    break_end = models.TimeField(null=True, blank=True, help_text="Break end time")
    is_available = models.BooleanField(default=True, help_text="Is this schedule active?")

    class Meta:
        unique_together = ('doctor', 'day_of_week')

    def __str__(self):
        return f"{self.doctor} - {self.day_of_week}: {self.start_time} to {self.end_time}"
