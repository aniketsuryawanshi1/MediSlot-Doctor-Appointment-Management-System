from django.contrib import admin
from .models import PatientProfile, Appointment, WaitingList

@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'date_of_birth', 'gender']
    search_fields = ['user__username']

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'appointment_date', 'status']
    list_filter = ['status', 'service_type']

@admin.register(WaitingList)
class WaitingListAdmin(admin.ModelAdmin):
    list_display = ['patient', 'doctor', 'requested_date']
    list_filter = ['is_notified']
