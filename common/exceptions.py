from rest_framework.exceptions import APIException


class AppointmentConflictError(APIException):
    """Raised when an appointment booking conflicts with existing schedules."""
    status_code = 409
    default_detail = "Appointment conflict: The selected slot is unavailable."
    default_code = "appointment_conflict"


class InvalidScheduleError(APIException):
    """Raised when a doctor's schedule is invalid (e.g., overlapping times)."""
    status_code = 400
    default_detail = "Invalid schedule: Please check working hours and breaks."
    default_code = "invalid_schedule"


class NotificationFailureError(APIException):
    """Raised when sending notifications (email/Telegram) fails."""
    status_code = 500
    default_detail = "Notification failed: Unable to send message."
    default_code = "notification_failure"


class AuthenticationError(APIException):
    """Raised for authentication-related issues (e.g., invalid OTP)."""
    status_code = 401
    default_detail = "Authentication failed: Invalid credentials or token."
    default_code = "authentication_error"