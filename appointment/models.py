from django.db import models
from django.core.exceptions import ValidationError
from mainapp.models import Doctor
from django.utils import timezone

# Assuming Doctor model already exists in the same app:
# from .models import Doctor

# -----------------------------
# Doctor Availability
# -----------------------------
class DoctorAvailability(models.Model):
    class Days(models.IntegerChoices):
        MONDAY = 1, "Monday"
        TUESDAY = 2, "Tuesday"
        WEDNESDAY = 3, "Wednesday"
        THURSDAY = 4, "Thursday"
        FRIDAY = 5, "Friday"
        SATURDAY = 6, "Saturday"
        SUNDAY = 7, "Sunday"

    doctor = models.ForeignKey(Doctor, on_delete=models.CASCADE, related_name="availabilities", verbose_name="Doctor")
    day_of_week = models.PositiveSmallIntegerField(choices=Days.choices, verbose_name="Day of week")
    start_time = models.TimeField(verbose_name="Start time")
    end_time = models.TimeField(verbose_name="End time")
    slot_minutes = models.PositiveSmallIntegerField(default=15, verbose_name="Slot duration (min)")
    max_patients_per_slot = models.PositiveSmallIntegerField(default=1, verbose_name="Max patients per slot")
    effective_from = models.DateField(blank=True, null=True, verbose_name="Effective from")
    effective_to = models.DateField(blank=True, null=True, verbose_name="Effective to")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Doctor Availability"
        verbose_name_plural = "Doctor Availabilities"
        ordering = ( "day_of_week", "start_time")
        constraints = [
            models.UniqueConstraint(fields=["doctor", "day_of_week", "start_time", "end_time"], name="uniq_doctor_day_time_block")
        ]

    def clean(self):
        if self.end_time <= self.start_time: raise ValidationError({"end_time": "End time must be after start time."})
        if self.slot_minutes == 0: raise ValidationError({"slot_minutes": "Slot duration must be > 0."})

    def __str__(self):
        return f"{self.doctor.name} • {self.get_day_of_week_display()} {self.start_time.strftime('%H:%M')}-{self.end_time.strftime('%H:%M')}"


# -----------------------------
# Appointments
# -----------------------------
class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        COMPLETED = "completed", "Completed"
        NO_SHOW = "no_show", "No Show"

    doctor = models.ForeignKey(Doctor, on_delete=models.PROTECT, related_name="appointments", verbose_name="Doctor")
    appointment_date = models.DateField(verbose_name="Date")
    start_time = models.TimeField(verbose_name="Start time")
    end_time = models.TimeField(verbose_name="End time")
    patient_name = models.CharField(max_length=150, verbose_name="Patient name")
    patient_phone = models.CharField(max_length=30, verbose_name="Patient phone")
    patient_email = models.EmailField(blank=True, null=True, verbose_name="Patient email")
    reason = models.CharField(max_length=200, blank=True, verbose_name="Reason (short)")
    notes = models.TextField(blank=True, verbose_name="Notes")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.PENDING, verbose_name="Status")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        ordering = ("-appointment_date", "start_time")
        indexes = [models.Index(fields=["doctor", "appointment_date", "start_time"])]
        constraints = [
            # Prevent exact duplicates; actual overlap checks done in clean()
            models.UniqueConstraint(fields=["doctor", "appointment_date", "start_time"], name="uniq_doctor_date_start")
        ]

    def clean(self):
        if self.end_time <= self.start_time: raise ValidationError({"end_time": "End time must be after start time."})
        # Basic business rule: can't book in the past (except editing completed)
        if self.status in {self.Status.PENDING, self.Status.CONFIRMED}:
            dt = timezone.make_aware(timezone.datetime.combine(self.appointment_date, self.start_time)) if timezone.is_naive(timezone.now()) else timezone.datetime.combine(self.appointment_date, self.start_time).replace(tzinfo=timezone.get_current_timezone())
            if dt < timezone.now(): raise ValidationError("Cannot book in the past.")
        # Optional: check that chosen time falls within a matching availability window
        dow = self.appointment_date.isoweekday()  # 1=Mon..7=Sun
        qs = DoctorAvailability.objects.filter(doctor=self.doctor, active=True, day_of_week=dow)
        if not qs.exists(): raise ValidationError("Doctor is not available on the selected day.")
        # Ensure the chosen times fall inside at least one availability block
        within_block = qs.filter(start_time__lte=self.start_time, end_time__gte=self.end_time).exists()
        if not within_block: raise ValidationError("Selected time does not fit the doctor's availability window.")
        # Prevent overlapping appointments for same doctor
        overlapping = Appointment.objects.exclude(pk=self.pk).filter(doctor=self.doctor, appointment_date=self.appointment_date, start_time__lt=self.end_time, end_time__gt=self.start_time, status__in=[self.Status.PENDING, self.Status.CONFIRMED]).exists()
        if overlapping: raise ValidationError("This time overlaps with another appointment.")

    def __str__(self):
        return f"{self.appointment_date} {self.start_time.strftime('%H:%M')} - {self.doctor.name} ({self.patient_name})"
