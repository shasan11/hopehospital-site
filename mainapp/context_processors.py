from datetime import datetime
from django.utils import timezone
from django.core.cache import cache
from .models import (
    Settings,
    Department, DepartmentService, Doctor,
    HealthPackage,
    TeamDepartment, TeamMember,
    BlogCategory, BlogTag, BlogPost,
    Notice,
    Gallery, GalleryPic,
    VideoAlbum, Video,
    Service,
    Content,
    WebsiteContent,LatestNews
)
CACHE_KEY = "global_site_context_v1"
CACHE_TTL = 300  
def _active_published_news_qs():
    now = timezone.now()
    return (
        BlogPost.objects.filter(
            status="published",
            active=True,
            published_at__isnull=False,
            published_at__lte=now,
        )
        .select_related("category", "author")
        .prefetch_related("tags")
        .order_by("-published_at", "priority", "title")
    )
def _active_notices_qs():
    now = timezone.now()
    return (
        Notice.objects.filter(
            active=True,
        )
        .filter(
        )
    )
def _notices_in_window():
    now = timezone.now()
    qs = Notice.objects.filter(active=True)
    return qs.filter(
        publish_start__lte=now if qs.filter(publish_start__isnull=False).exists() else None,
    ) | qs.filter(publish_start__isnull=True)
def _compute_context():
    now = timezone.now()
    site_settings = Settings.objects.first()
    website_content=WebsiteContent.objects.first()
    nav_departments = Department.objects.filter(active=True).order_by("priority", "name")
    nav_services = Service.objects.all().order_by("priority", "name")  
    doctors_qs = Doctor.objects.filter(active=True)
    team_departments = TeamDepartment.objects.filter(active=True).order_by("priority",)
    team_members = TeamMember.objects.filter(active=True).select_related("department").order_by("priority")
    health_packages = HealthPackage.objects.filter(active=True).order_by("priority", "name")
    galleries = Gallery.objects.filter(active=True).order_by("priority", "name")
    video_albums = VideoAlbum.objects.filter(active=True).order_by("priority", "name")
    blog_categories = BlogCategory.objects.filter(active=True).order_by("priority", "name")
    blog_tags = BlogTag.objects.all().order_by("name")
    latest_blog_posts = BlogPost.objects.filter(status="published").order_by("is_featured") 
    active_notices = Notice.objects.filter(active=True)
    notices_in_window = active_notices.filter(
        publish_start__lte=now
    ) | active_notices.filter(publish_start__isnull=True)
    notices_in_window = notices_in_window.filter(publish_end__gte=now) | notices_in_window.filter(publish_end__isnull=True)
    notices_in_window = notices_in_window.order_by("priority", "-publish_start", "title")
    popup_notice = notices_in_window.filter(popup_on_homepage=True).order_by("priority", "-publish_start").first()
    latest_news =LatestNews.objects.all()
    top_contents = Content.objects.filter(parent__isnull=True).order_by("priority", "title")
    return {
        "site_settings": site_settings,
        "nav_departments": nav_departments,
        "nav_services": nav_services,
        "nav_doctors": doctors_qs,
        "nav_team_departments": team_departments,
        "nav_team_members": team_members,
        "nav_health_packages": health_packages,
        "nav_galleries": galleries,
        "nav_video_albums": video_albums,
        "blog_categories": blog_categories,
        "blog_tags": blog_tags,
        "latest_blog_posts": latest_blog_posts,
        "latest_news_items": latest_news,
        "active_notices": notices_in_window,
        "homepage_popup_notice": popup_notice,
        "top_contents": top_contents,
        "website_content": website_content,
    }
def global_site_context(request):
    """
    Adds globally useful QuerySets/objects into all templates.
    Lightly cached to reduce per-request DB work.
    """
    data = cache.get(CACHE_KEY)
    if data is None:
        data = _compute_context()
        cache.set(CACHE_KEY, data, CACHE_TTL)
    return data
