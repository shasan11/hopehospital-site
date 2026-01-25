from django.shortcuts import render, get_object_or_404
from .models import (
    Department, DepartmentService, Doctor, HealthPackage,
    TeamDepartment, TeamMember, BlogPost, BlogCategory, BlogTag,
    Notice, Gallery, GalleryPic, VideoAlbum, Video,
    LatestNews, Service, Content
)


# -----------------------------
# Static Pages
# -----------------------------
def home(request):
    return render(request, "website/index.html")


def services(request):
    return render(request, "website/services.html")

def about_intro(request):
    return render(request, "website/about_intro.html")

def mission_vision(request):
    return render(request, "website/mission_vision.html")

def core_values(request):
    return render(request, "website/core_values.html")

def chairman_message(request):
    return render(request, "website/chairman_message.html")

def md_message(request):
    return render(request, "website/md_message.html")

def contact(request):
    return render(request, "website/contact.html")

def appointment(request):
    return render(request, "website/appointment.html")

def track_appointment(request):
    return render(request, "website/track_appointment.html")

def handler404(request,exception):
    return render(request, "website/404.html",status=404)


# -----------------------------
# Departments
# -----------------------------
def department(request):
    items = Department.objects.filter(active=True)
    return render(request, "website/department.html", {"departments": items})

from django.shortcuts import render, get_object_or_404
from .models import Department, Doctor, DepartmentService

def department_details(request, slug):
    department = get_object_or_404(Department, slug=slug, active=True)
    doctors = Doctor.objects.filter(department=department, active=True).order_by('priority', 'name')
    dept_services = DepartmentService.objects.filter(department=department, active=True).order_by('priority', 'name')
    
    # Render template with context
    context = {
        "department": department,
        "doctors": doctors,
        "dept_services": dept_services,
    }
    return render(request, "website/department_details.html", context)



# -----------------------------
# Doctors
# -----------------------------
def doctors(request):
    items = Doctor.objects.filter(active=True)
    return render(request, "website/doctors.html", {"doctors": items})

def doctor_details(request, slug):
    item = get_object_or_404(Doctor, slug=slug, active=True)
    return render(request, "website/doctor_details.html", {"doctor": item})


# -----------------------------
# Services
# -----------------------------
def services_details(request, slug):
    item = get_object_or_404(Service, slug=slug)
    return render(request, "website/services_details.html", {"service": item})


# -----------------------------
# Health Packages
# -----------------------------
def packages(request):
    items = HealthPackage.objects.filter(active=True)
    return render(request, "website/packages.html", {"packages": items})

def packages_details(request, slug):
    item = get_object_or_404(HealthPackage, slug=slug, active=True)
    return render(request, "website/packages_details.html", {"package": item})


# -----------------------------
# Blogs
# -----------------------------
def blogs(request):
    items = BlogPost.objects.filter(status="published", active=True)
    return render(request, "website/blogs.html", {"blogs": items})

def blogs_details(request, slug):
    item = get_object_or_404(BlogPost, slug=slug, status="published", active=True)
    return render(request, "website/blogs_details.html", {"blog": item})


# -----------------------------
# Gallery
# -----------------------------
def gallery(request):
    items = Gallery.objects.filter(active=True)
    return render(request, "website/gallery.html", {"galleries": items})

def gallery_details(request, slug):
    item = get_object_or_404(Gallery, slug=slug, active=True)
    return render(request, "website/gallery_details.html", {"gallery": item})



# -----------------------------
# Team
# -----------------------------
def team(request):
    items = TeamMember.objects.filter(active=True)
    return render(request, "website/team.html", {"team_members": items})

def bod(request):
    return render(request, "website/bod.html")


# -----------------------------
# Careers, News, Notices
# -----------------------------
def careers(request):
    return render(request, "website/careers.html")

def latest_news(request):
    items = LatestNews.objects.filter(status="published", active=True)
    return render(request, "website/latest_news.html", {"news_list": items})

def latest_news_details(request, slug):
    item = get_object_or_404(
        LatestNews,
        slug=slug,
        status="published",
        active=True
    )
    return render(request, "website/latest_news_details.html", {"news": item})