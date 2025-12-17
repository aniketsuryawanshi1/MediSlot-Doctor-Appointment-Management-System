from django.urls import path
from .views import (
    DoctorProfileListCreateView, DoctorProfileDetailView,
    ScheduleListCreateView, ScheduleDetailView, ScheduleAvailableSlotsView,
    AppointmentListView, AppointmentDetailView, AppointmentConfirmView
)

urlpatterns = [
    # Doctor Profile Endpoints
    path('profiles/', DoctorProfileListCreateView.as_view(), name='doctor-profile-list-create'),
    path('profiles/<uuid:pk>/', DoctorProfileDetailView.as_view(), name='doctor-profile-detail'),

    # Schedule Endpoints
    path('schedules/', ScheduleListCreateView.as_view(), name='schedule-list-create'),
    path('schedules/<uuid:pk>/', ScheduleDetailView.as_view(), name='schedule-detail'),
    path('schedules/available-slots/', ScheduleAvailableSlotsView.as_view(), name='schedule-available-slots'),

    # Appointment Endpoints (Doctor-side)
    path('appointments/', AppointmentListView.as_view(), name='appointment-list'),
    path('appointments/<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<uuid:pk>/confirm/', AppointmentConfirmView.as_view(), name='appointment-confirm'),
]