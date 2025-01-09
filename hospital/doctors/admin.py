from django.contrib import admin

from .models import Doctor, Schedule, Appointment


@admin.register(Doctor)
class DoctorAdmin(admin.ModelAdmin):
    list_display = ("name", "office", "slug", "specialization")
    list_editable = ("specialization",)
    search_fields = ("name", "specialization", "office")
    prepopulated_fields = {"slug": ("office",)}


@admin.register(Schedule)
class ScheduleAdmin(admin.ModelAdmin):
    list_display = ("doctor", "day_of_week", "start_time", "end_time", "office")
    list_editable = ("office",)
    list_filter = ("doctor", "day_of_week")


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ("doctor", "patient", "date", "time", "status")
    list_editable = ("status",)
    list_filter = ("doctor", "date", "status")
