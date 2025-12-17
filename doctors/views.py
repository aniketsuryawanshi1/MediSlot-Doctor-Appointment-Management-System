from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import DoctorProfile, Schedule
from .serializers import DoctorProfileSerializer, ScheduleSerializer
from .services.doctor_service import DoctorService
from .services.schedule_service import ScheduleService
from .services.appointment_service import AppointmentService
from patients.serializers import AppointmentSerializer
from patients.models import Appointment
from common.permissions import IsAuthenticatedAndActive
from .utils.validators import validate_profile, validate_schedule  # Used for validation
from .utils.constants import SPECIALTIES  # Used for checks
from .utils.helpers import format_slot_display  # Used for formatting
from common.exceptions import InvalidScheduleError  # Added

class DoctorProfileListCreateView(APIView):
    """List and create doctor profiles."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        profiles = DoctorProfile.objects.filter(user=request.user)
        serializer = DoctorProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        validate_profile(request.data)  # Use validator
        service = DoctorService()
        try:
            profile = service.create_profile(request.user, **request.data)
            serializer = DoctorProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class DoctorProfileDetailView(APIView):
    """Retrieve, update, delete doctor profile."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        profile = get_object_or_404(DoctorProfile, pk=pk, user=request.user)
        serializer = DoctorProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        profile = get_object_or_404(DoctorProfile, pk=pk, user=request.user)
        validate_profile(request.data)  # Use validator
        service = DoctorService()
        try:
            updated_profile = service.update_profile(profile, request.data)
            serializer = DoctorProfileSerializer(updated_profile)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = get_object_or_404(DoctorProfile, pk=pk, user=request.user)
        service = DoctorService()
        service.delete_profile(profile)
        return Response(status=status.HTTP_204_NO_CONTENT)

class ScheduleListCreateView(APIView):
    """List and create schedules."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        schedules = Schedule.objects.filter(doctor=doctor)
        serializer = ScheduleSerializer(schedules, many=True)
        return Response(serializer.data)

    def post(self, request):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        validate_schedule(request.data)  # Use validator
        service = ScheduleService()
        try:
            schedule = service.create_schedule(doctor, request.data)
            serializer = ScheduleSerializer(schedule)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class ScheduleDetailView(APIView):
    """Retrieve, update, delete schedule."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        schedule = get_object_or_404(Schedule, pk=pk, doctor=doctor)
        serializer = ScheduleSerializer(schedule)
        return Response(serializer.data)

    def put(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        schedule = get_object_or_404(Schedule, pk=pk, doctor=doctor)
        validate_schedule(request.data)  # Use validator
        service = ScheduleService()
        try:
            updated_schedule = service.update_schedule(schedule, request.data)
            serializer = ScheduleSerializer(updated_schedule)
            return Response(serializer.data)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        schedule = get_object_or_404(Schedule, pk=pk, doctor=doctor)
        schedule.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ScheduleAvailableSlotsView(APIView):
    """Get available slots."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        date_str = request.query_params.get('date')
        if not date_str:
            return Response({"error": "Date required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            date = timezone.datetime.fromisoformat(date_str).date()
        except ValueError:
            return Response({"error": "Invalid date format"}, status=status.HTTP_400_BAD_REQUEST)
        service = ScheduleService()
        slots = service.get_available_slots(doctor, date)
        formatted_slots = [format_slot_display(start, end) for start, end in slots]  # Use helper
        return Response({"available_slots": formatted_slots})

class AppointmentListView(APIView):
    """List doctor's appointments."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        service = AppointmentService()
        appointments = service.get_appointments(doctor)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

class AppointmentDetailView(APIView):
    """Retrieve appointment."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

class AppointmentConfirmView(APIView):
    """Confirm appointment."""
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, pk):
        doctor = get_object_or_404(DoctorProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, doctor=doctor)
        service = AppointmentService()
        try:
            service.confirm_appointment(appointment)
            return Response({"message": "Appointment confirmed"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
