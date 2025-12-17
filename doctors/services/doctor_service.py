# Updated to use validators.
from ..models import DoctorProfile
from ..serializers import DoctorProfileSerializer
from common.exceptions import InvalidScheduleError
from ..utils.validators import validate_profile  # Added


class DoctorProfileFactory:
    """Factory for creating DoctorProfile instances (GOF: Factory Pattern)."""
    @staticmethod
    def create_profile(user, specialty, license_number, **kwargs):
        if DoctorProfile.objects.filter(license_number=license_number).exists():
            raise ValueError("License number already exists.")
        profile = DoctorProfile.objects.create(
            user=user, specialty=specialty, license_number=license_number, **kwargs
        )
        return profile


class DoctorService:
    """Service for doctor profile operations."""
    def get_profile(self, user):
        """Retrieve doctor profile."""
        return DoctorProfile.objects.filter(user=user).first()

    def update_profile(self, profile, data):
        """Update doctor profile."""
        serializer = DoctorProfileSerializer(profile, data=data, partial=True)
        if serializer.is_valid():
            return serializer.save()
        raise InvalidScheduleError(serializer.errors)

    def delete_profile(self, profile):
        """Soft delete doctor profile."""
        profile.soft_delete()

    def create_profile(self, user, **data):
        validate_profile(data)  # Use validator