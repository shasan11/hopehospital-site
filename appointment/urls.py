from django.urls import path
from . import views

urlpatterns = [
    # Pages
    path("appointment/online/", views.appointment_page, name="appointment"),
    path("appointment/track/", views.track_appointment_page, name="appointment_track"),

    # APIs
    path("api/appointment/doctors/", views.api_doctors, name="api_doctors"),
    path("api/appointment/slots/", views.api_slots, name="api_slots"),
    path("api/appointment/create/", views.api_create_appointment, name="api_create_appointment"),
    path("api/appointment/track/", views.api_track_appointment, name="api_track_appointment"),
]
