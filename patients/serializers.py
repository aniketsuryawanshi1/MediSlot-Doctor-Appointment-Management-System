from rest_framework import serializers
from .models import PatientProfile, Appointment, WaitingList
from doctors.models import DoctorProfile
from common.exceptions import AppointmentConflictError


class PatientProfileSerializer(serializers.ModelSerializer):
    """Serializer for patient profiles."""
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = PatientProfile
        fields = [
            'id', 'user', 'date_of_birth', 'gender', 'emergency_contact',
            'emergency_phone', 'medical_history', 'user_full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AppointmentSerializer(serializers.ModelSerializer):
    """Serializer for appointments with conflict checks."""
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'patient', 'doctor', 'appointment_date', 'start_time', 'end_time',
            'service_type', 'status', 'notes', 'appointment_id', 'patient_name', 'doctor_name',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'appointment_id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate for overlaps and availability (GOF: Strategy for booking logic)."""
        doctor = data.get('doctor')
        date = data.get('appointment_date')
        start = data.get('start_time')
        end = data.get('end_time')
        if Appointment.objects.filter(
            doctor=doctor, appointment_date=date,
            start_time__lt=end, end_time__gt=start
        ).exclude(pk=self.instance.pk if self.instance else None).exists():
            raise AppointmentConflictError("Appointment overlaps with existing booking.")
        return data


class WaitingListSerializer(serializers.ModelSerializer):
    """Serializer for waiting lists."""
    patient_name = serializers.CharField(source='patient.user.get_full_name', read_only=True)
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = WaitingList
        fields = [
            'id', 'patient', 'doctor', 'requested_date', 'requested_time',
            'notes', 'is_notified', 'patient_name', 'doctor_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']