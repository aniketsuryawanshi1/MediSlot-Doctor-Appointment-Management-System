from rest_framework import serializers
from .models import DoctorProfile, Schedule
from common.exceptions import InvalidScheduleError


class DoctorProfileSerializer(serializers.ModelSerializer):
    """Serializer for doctor profiles."""
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)

    class Meta:
        model = DoctorProfile
        fields = [
            'id', 'user', 'specialty', 'license_number', 'experience_years',
            'contact_phone', 'bio', 'user_full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ScheduleSerializer(serializers.ModelSerializer):
    """Serializer for doctor schedules with validation for conflicts."""
    doctor_name = serializers.CharField(source='doctor.user.get_full_name', read_only=True)

    class Meta:
        model = Schedule
        fields = [
            'id', 'doctor', 'day_of_week', 'start_time', 'end_time',
            'break_start', 'break_end', 'is_available', 'doctor_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

    def validate(self, data):
        """Validate schedule for overlaps or invalid times (GOF: Strategy for validation)."""
        start = data.get('start_time')
        end = data.get('end_time')
        break_start = data.get('break_start')
        break_end = data.get('break_end')
        if start and end and start >= end:
            raise InvalidScheduleError("Start time must be before end time.")
        if break_start and break_end and (break_start < start or break_end > end):
            raise InvalidScheduleError("Break times must be within working hours.")
        return data