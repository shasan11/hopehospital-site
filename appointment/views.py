from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from mainapp.models import Doctor
from .models import DoctorAvailability, Appointment


# -----------------------------
# Page Views
# -----------------------------
def appointment_page(request):
    """Online Appointment page (Angular-driven)."""
    return render(request, "appointment/appointment.html")


def track_appointment_page(request):
    """Track Appointment page (Angular-driven)."""
    return render(request, "appointment/track_appointment.html")


# -----------------------------
# Helpers
# -----------------------------
def _fmt_code(id_val: int) -> str:
    return f"APT-{id_val:06d}"

def _parse_code(code: str) -> int | None:
    try:
        prefix, num = code.split("-")
        if prefix.upper() != "APT":
            return None
        return int(num)
    except Exception:
        return None

def _slots_for_date(doctor: Doctor, date_obj):
    """
    Build available slots for doctor/date based on DoctorAvailability and existing appointments.
    """
    dow = date_obj.isoweekday()  # 1=Mon..7=Sun
    blocks = DoctorAvailability.objects.filter(
        doctor=doctor, active=True, day_of_week=dow
    ).order_by("start_time")

    if not blocks.exists():
        return []

    existing = set(
        Appointment.objects.filter(
            doctor=doctor,
            appointment_date=date_obj,
            status__in=[Appointment.Status.PENDING, Appointment.Status.CONFIRMED],
        ).values_list("start_time", flat=True)
    )

    slots = []
    now_local = timezone.localtime()
    tz = timezone.get_current_timezone()

    for b in blocks:
        # effective window checks
        if b.effective_from and date_obj < b.effective_from:
            continue
        if b.effective_to and date_obj > b.effective_to:
            continue

        cursor = datetime.combine(date_obj, b.start_time)
        end_dt = datetime.combine(date_obj, b.end_time)
        step = timedelta(minutes=b.slot_minutes)

        while cursor + step <= end_dt:
            start_t = cursor.time()
            end_t = (cursor + step).time()

            slot_dt = datetime.combine(date_obj, start_t).replace(tzinfo=tz)
            if slot_dt < now_local:
                cursor += step
                continue

            if start_t not in existing:
                slots.append({
                    "start_time": start_t.strftime("%H:%M"),
                    "end_time": end_t.strftime("%H:%M"),
                })
            cursor += step

    return slots


# -----------------------------
# JSON APIs
# -----------------------------
@require_GET
def api_doctors(request):
    qs = Doctor.objects.all().order_by("priority" if hasattr(Doctor, "priority") else "name")
    data = [
        {
            "id": d.id,
            "name": getattr(d, "name", str(d)),
            "department": getattr(d.department, "name", "") if getattr(d, "department", None) else "",
        }
        for d in qs
    ]
    return JsonResponse({"doctors": data})


@require_GET
def api_slots(request):
    doctor_id = request.GET.get("doctor_id")
    date_str = request.GET.get("date")
    if not doctor_id or not date_str:
        return HttpResponseBadRequest("doctor_id and date are required")

    doctor = get_object_or_404(Doctor, pk=doctor_id)

    try:
        date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return HttpResponseBadRequest("Invalid date format (YYYY-MM-DD)")

    slots = _slots_for_date(doctor, date_obj)
    return JsonResponse({"slots": slots})


@csrf_exempt  # for simplicity; in prod, include CSRF token in AJAX calls
@require_POST
def api_create_appointment(request):
    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    required = ["doctor_id", "date", "start_time", "patient_name", "patient_phone"]
    missing = [k for k in required if not payload.get(k)]
    if missing:
        return HttpResponseBadRequest(f"Missing fields: {', '.join(missing)}")

    doctor = get_object_or_404(Doctor, pk=payload["doctor_id"])

    try:
        date_obj = datetime.strptime(payload["date"], "%Y-%m-%d").date()
        st = datetime.strptime(payload["start_time"], "%H:%M").time()
    except ValueError:
        return HttpResponseBadRequest("Invalid date or time format")

    # derive end_time from availability slot_minutes (default 15)
    block = DoctorAvailability.objects.filter(
        doctor=doctor,
        active=True,
        day_of_week=date_obj.isoweekday(),
        start_time__lte=st,
        end_time__gt=st,
    ).order_by("start_time").first()

    slot_minutes = block.slot_minutes if block else 15
    et = (datetime.combine(date_obj, st) + timedelta(minutes=slot_minutes)).time()

    appt = Appointment(
        doctor=doctor,
        appointment_date=date_obj,
        start_time=st,
        end_time=et,
        patient_name=payload["patient_name"],
        patient_phone=payload["patient_phone"],
        patient_email=payload.get("patient_email") or None,
        reason=(payload.get("reason") or "")[:200],
        notes="",
        status=Appointment.Status.PENDING,
    )

    from django.core.exceptions import ValidationError
    try:
        appt.full_clean()
        appt.save()
    except ValidationError as e:
        return JsonResponse(
            {"ok": False, "errors": e.message_dict if hasattr(e, "message_dict") else e.messages},
            status=400
        )

    code = _fmt_code(appt.id)

    # Email code if provided
    if appt.patient_email:
        subject = f"Your Appointment #{code}"
        body = (
            f"Dear {appt.patient_name},\n\n"
            f"Your appointment has been created.\n\n"
            f"Appointment No: {code}\n"
            f"Doctor: {appt.doctor.name}\n"
            f"Date: {appt.appointment_date.strftime('%Y-%m-%d')}\n"
            f"Time: {appt.start_time.strftime('%H:%M')} - {appt.end_time.strftime('%H:%M')}\n\n"
            f"Thank you."
        )
        try:
            send_mail(
                subject,
                body,
                getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
                [appt.patient_email],
                fail_silently=True,
            )
        except Exception:
            pass

    return JsonResponse({"ok": True, "appointment_code": code})


@csrf_exempt  # for simplicity; in prod, include CSRF token in AJAX calls
@require_POST
def api_track_appointment(request):
    import json
    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return HttpResponseBadRequest("Invalid JSON")

    code = (payload.get("code") or "").strip()
    appt_id = _parse_code(code)
    if not appt_id:
        return HttpResponseBadRequest("Invalid appointment code")

    appt = Appointment.objects.filter(pk=appt_id).select_related("doctor").first()
    if not appt:
        return JsonResponse({"ok": False, "message": "Appointment not found"}, status=404)

    return JsonResponse({
        "ok": True,
        "appointment": {
            "code": code,
            "doctor": getattr(appt.doctor, "name", str(appt.doctor)),
            "date": appt.appointment_date.strftime("%Y-%m-%d"),
            "start_time": appt.start_time.strftime("%H:%M"),
            "end_time": appt.end_time.strftime("%H:%M"),
            "patient_name": appt.patient_name,
            "status": appt.status,
            "created_at": timezone.localtime(appt.created_at).strftime("%Y-%m-%d %H:%M"),
        }
    })
