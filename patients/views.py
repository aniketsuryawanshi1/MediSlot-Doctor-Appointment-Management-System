from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from .models import PatientProfile, Appointment, WaitingList
from .serializers import PatientProfileSerializer, AppointmentSerializer, WaitingListSerializer
from .services.booking_service import BookingService
from .services.notification_service import NotificationService
from common.permissions import IsAuthenticatedAndActive
from .utils.validators import validate_appointment, validate_profile
from .utils.constants import CANCELLATION_POLICY_HOURS
from django.utils import timezone
from common.exceptions import AppointmentConflictError

class PatientProfileListCreateView(APIView):
    """List and create patient profiles."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        profiles = PatientProfile.objects.filter(user=request.user)
        serializer = PatientProfileSerializer(profiles, many=True)
        return Response(serializer.data)

    def post(self, request):
        validate_profile(request.data)
        serializer = PatientProfileSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class PatientProfileDetailView(APIView):
    """Retrieve, update, delete patient profile."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        profile = get_object_or_404(PatientProfile, pk=pk, user=request.user)
        serializer = PatientProfileSerializer(profile)
        return Response(serializer.data)

    def put(self, request, pk):
        profile = get_object_or_404(PatientProfile, pk=pk, user=request.user)
        validate_profile(request.data)
        serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        profile = get_object_or_404(PatientProfile, pk=pk, user=request.user)
        profile.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class AppointmentListCreateView(APIView):
    """List and book appointments."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        patient = get_object_or_404(PatientProfile, user=request.user)
        appointments = Appointment.objects.filter(patient=patient)
        serializer = AppointmentSerializer(appointments, many=True)
        return Response(serializer.data)

    def post(self, request):
        patient = get_object_or_404(PatientProfile, user=request.user)
        validate_appointment(request.data)
        service = BookingService()
        try:
            appointment = service.book_appointment(patient, request.data)
            serializer = AppointmentSerializer(appointment)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        except AppointmentConflictError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AppointmentDetailView(APIView):
    """Retrieve appointment."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        patient = get_object_or_404(PatientProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
        serializer = AppointmentSerializer(appointment)
        return Response(serializer.data)

class AppointmentCancelView(APIView):
    """Cancel appointment."""
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, pk):
        patient = get_object_or_404(PatientProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
        service = BookingService()
        try:
            service.cancel_appointment(appointment)
            return Response({"message": "Appointment canceled"})
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class AppointmentRescheduleView(APIView):
    """Reschedule appointment."""
    permission_classes = [IsAuthenticatedAndActive]

    def post(self, request, pk):
        patient = get_object_or_404(PatientProfile, user=request.user)
        appointment = get_object_or_404(Appointment, pk=pk, patient=patient)
        service = BookingService()
        try:
            new_appointment = service.reschedule_appointment(appointment, request.data)
            serializer = AppointmentSerializer(new_appointment)
            return Response(serializer.data)
        except AppointmentConflictError as e:
            return Response({"error": str(e)}, status=status.HTTP_409_CONFLICT)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

class WaitingListListCreateView(APIView):
    """List and join waiting list."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request):
        patient = get_object_or_404(PatientProfile, user=request.user)
        waiting_list = WaitingList.objects.filter(patient=patient)
        serializer = WaitingListSerializer(waiting_list, many=True)
        return Response(serializer.data)

    def post(self, request):
        patient = get_object_or_404(PatientProfile, user=request.user)
        serializer = WaitingListSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(patient=patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class WaitingListDetailView(APIView):
    """Retrieve waiting list entry."""
    permission_classes = [IsAuthenticatedAndActive]

    def get(self, request, pk):
        patient = get_object_or_404(PatientProfile, user=request.user)
        entry = get_object_or_404(WaitingList, pk=pk, patient=patient)
        serializer = WaitingListSerializer(entry)
        return Response(serializer.data)
