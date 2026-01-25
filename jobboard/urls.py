# jobboard/urls.py
from django.urls import path
from .views import CareersListView, CareerDetailView

urlpatterns = [
    path("careers/", CareersListView.as_view(), name="careers"),
    path("careers/<slug:slug>/", CareerDetailView.as_view(), name="career_detail"),
]
