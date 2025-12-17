from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import status
from patients.models import PatientProfile
from doctors.models import DoctorProfile

User = get_user_model()


class AuthenticationMiddleware:
    """
    Custom middleware to enforce authentication and role checks on every request.
    Attaches user_role to request if valid (GOF: Chain of Responsibility).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip auth checks for public endpoints (e.g., login, register)
        public_paths = ['/auth/login/', '/auth/register/', '/admin/']  # Adjust as needed
        if any(request.path.startswith(path) for path in public_paths):
            return self.get_response(request)

        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse(
                {"error": "Authentication required."},
                status=status.HTTP_401_UNAUTHORIZED
            )

        # Check for valid role (patient or doctor profile exists)
        user = request.user
        if hasattr(user, 'patient_profile') and user.patient_profile:
            request.user_role = 'patient'
        elif hasattr(user, 'doctor_profile') and user.doctor_profile:
            request.user_role = 'doctor'
        else:
            return JsonResponse(
                {"error": "Invalid user role. Must be patient or doctor."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Proceed with the request
        response = self.get_response(request)
        return response