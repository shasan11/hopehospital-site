from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about-us/', views.about_intro, name='about_intro'),
    path('mission-vision/', views.mission_vision, name='mission_vision'),
    path('core-values/', views.core_values, name='core_values'),
    path('chairman-message/', views.chairman_message, name='chairman_message'),
    path('managing-director-message/', views.md_message, name='md_message'),
    path('bod/', views.bod, name='bod'),
    path('team/', views.team, name='team'),
    path('department/', views.department, name='department'),
    path('department-details/<slug:slug>', views.department_details, name='department_details'),
    path('doctors/', views.doctors, name='doctors'),
    path('doctor-details/<slug:slug>/', views.doctor_details, name='doctor_details'),
    path('services/', views.services, name='services'),
    path('services-details/<slug:slug>', views.services_details, name='services_details'),
    path('packages/', views.packages, name='packages'),
    path('packages-details/<slug:slug>/', views.packages_details, name='packages_details'),
    path('latest-news/', views.latest_news, name='latest_news'),
    path("latest-news/<slug:slug>/", views.latest_news_details, name="latest_news_details"),
    path('blogs/', views.blogs, name='blogs'),
    path('blogs-details/<slug:slug>', views.blogs_details, name='blogs_details'),
    path('gallery/', views.gallery, name='gallery'),
    path('gallery-details/<slug:slug>/', views.gallery_details, name='gallery_details'),
    path('contact/', views.contact, name='contact'),
]
