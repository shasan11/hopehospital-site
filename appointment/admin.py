# admin.py
from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline
from appointment.models import DoctorAvailability, Appointment
 
# ------------------------
# Inlines
# ------------------------
class DoctorAvailabilityInline(TabularInline):
    model = DoctorAvailability
    extra = 1
    fields = ("day_of_week", "start_time", "end_time", "slot_minutes", "max_patients_per_slot", "effective_from", "effective_to", "active", "priority")
    show_change_link = True

# (Optional) If you want to see a very compact appointment list inside Doctor, uncomment below.
# class AppointmentInline(TabularInline):
#     model = Appointment
#     extra = 0
#     fields = ("appointment_date", "start_time", "end_time", "patient_name", "status")
#     readonly_fields = ("appointment_date", "start_time", "end_time", "patient_name", "status")
#     can_delete = False
#     show_change_link = True

 
@admin.register(DoctorAvailability)
class DoctorAvailabilityAdmin(UnfoldModelAdmin):
    list_display = ("doctor", "day_of_week", "start_time", "end_time", "slot_minutes", "max_patients_per_slot", "effective_from", "effective_to", "active", "priority")
    list_filter = ("doctor", "day_of_week", "active")
    
    ordering = ("day_of_week", "start_time")
    fieldsets = ((None, {"fields": ("doctor", "day_of_week", "start_time", "end_time", "slot_minutes", "max_patients_per_slot", "effective_from", "effective_to", "active", "priority")}),)

@admin.register(Appointment)
class AppointmentAdmin(UnfoldModelAdmin):
    list_display = ("appointment_date", "start_time", "end_time", "doctor", "patient_name", "patient_phone", "status", "active")
    list_filter = ("status", "doctor", "appointment_date", "active")
    search_fields = ("patient_name", "patient_phone", "patient_email", "reason", "notes")
    ordering = ("-appointment_date", "start_time")
    readonly_fields = ("created_at", "updated_at")
    fieldsets = (
        ("Appointment", {"fields": ("doctor", "appointment_date", "start_time", "end_time", "status", "active")}),
        ("Patient", {"fields": ("patient_name", "patient_phone", "patient_email")}),
        ("Details", {"fields": ("reason", "notes")}),
        ("Timestamps", {"fields": ("created_at", "updated_at")}),
    )
