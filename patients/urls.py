from django.urls import path
from .views import (
    PatientProfileListCreateView, PatientProfileDetailView,
    AppointmentListCreateView, AppointmentDetailView, AppointmentCancelView, AppointmentRescheduleView,
    WaitingListListCreateView, WaitingListDetailView
)

urlpatterns = [
    # Patient Profile Endpoints
    path('profiles/', PatientProfileListCreateView.as_view(), name='patient-profile-list-create'),
    path('profiles/<uuid:pk>/', PatientProfileDetailView.as_view(), name='patient-profile-detail'),

    # Appointment Endpoints
    path('appointments/', AppointmentListCreateView.as_view(), name='appointment-list-create'),
    path('appointments/<uuid:pk>/', AppointmentDetailView.as_view(), name='appointment-detail'),
    path('appointments/<uuid:pk>/cancel/', AppointmentCancelView.as_view(), name='appointment-cancel'),
    path('appointments/<uuid:pk>/reschedule/', AppointmentRescheduleView.as_view(), name='appointment-reschedule'),

    # Waiting List Endpoints
    path('waiting-list/', WaitingListListCreateView.as_view(), name='waiting-list-list-create'),
    path('waiting-list/<uuid:pk>/', WaitingListDetailView.as_view(), name='waiting-list-detail'),
]