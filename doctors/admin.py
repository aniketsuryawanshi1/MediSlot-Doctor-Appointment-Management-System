from django.contrib import admin
from .models import DoctorProfile, Schedule

@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialty', 'license_number', 'experience_years']
    search_fields = ['user__username', 'specialty']

@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ['doctor', 'day_of_week', 'start_time', 'end_time', 'is_available']
    list_filter = ['day_of_week', 'is_available']
