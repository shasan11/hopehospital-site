from django.db import models
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.conf import settings
from tinymce.models import HTMLField


class Department(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Department name")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    icon = models.ImageField(upload_to="departments/icons/", blank=True, null=True, verbose_name="Icon")
    description = HTMLField(blank=True, verbose_name="Description")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class DepartmentService(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name="services", verbose_name="Department")
    name = models.CharField(max_length=150, verbose_name="Service name")
    slug = models.SlugField(max_length=160, verbose_name="Slug", blank=True, help_text="URL-friendly identifier (optional)")
    description = HTMLField(blank=True, verbose_name="Description")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Department Service"
        verbose_name_plural = "Department Services"
        ordering = ("priority", "name")
        constraints = [models.UniqueConstraint(fields=["department", "name"], name="uniq_service_name_per_department")]

    def __str__(self):
        return f"{self.name} ({self.department.name})"


class Doctor(models.Model):
    name = models.CharField(max_length=150, verbose_name="Doctor name")
    image = models.ImageField(upload_to="doctor/images", blank=True, null=True)
    position=models.CharField(max_length=100,default="Doctor")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors", verbose_name="Department")
    active = models.BooleanField(default=True, verbose_name="Active")
    description = HTMLField(blank=True, verbose_name="Description / Bio")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Doctor"
        verbose_name_plural = "Doctors"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('doctor_details', args=[self.slug])


class HealthPackage(models.Model):
    name = models.CharField(max_length=180, unique=True, verbose_name="Package name")
    description = HTMLField(blank=True, verbose_name="Description")
    slug = models.SlugField(max_length=190, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Price")
    image = models.ImageField(upload_to="health_packages/images/", blank=True, null=True, verbose_name="Image")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Health Package"
        verbose_name_plural = "Health Packages"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class TeamDepartment(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Department name")
    description = HTMLField(blank=True, verbose_name="Description")
    icon = models.ImageField(upload_to="team_departments/icons/", blank=True, null=True, verbose_name="Icon")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Team Department"
        verbose_name_plural = "Team Departments"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class TeamMember(models.Model):
    name = models.CharField(max_length=150, verbose_name="Member name")
    pic = models.ImageField(upload_to="team_members/photos/", blank=True, null=True, verbose_name="Picture")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    description = HTMLField(blank=True, verbose_name="Description")
    designation = models.CharField(max_length=150, blank=True, verbose_name="Designation")
    department = models.ForeignKey(TeamDepartment, on_delete=models.SET_NULL, null=True, blank=True, related_name="members", verbose_name="Department")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    active = models.BooleanField(default=True, verbose_name="Active")

    class Meta:
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class BlogCategory(models.Model):
    name = models.CharField(max_length=120, unique=True, verbose_name="Category name")
    slug = models.SlugField(max_length=140, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    description = HTMLField(blank=True, verbose_name="Description")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Blog Category"
        verbose_name_plural = "Blog Categories"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class BlogTag(models.Model):
    name = models.CharField(max_length=80, unique=True, verbose_name="Tag")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="Slug")

    class Meta:
        verbose_name = "Blog Tag"
        verbose_name_plural = "Blog Tags"
        ordering = ("name",)

    def __str__(self):
        return self.name


class BlogPost(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=180, verbose_name="Title")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug", help_text="URL-friendly unique identifier")
    subtitle = models.CharField(max_length=220, blank=True, verbose_name="Subtitle")
    author = models.ForeignKey(getattr(settings, "AUTH_USER_MODEL", "auth.User"), on_delete=models.SET_NULL, null=True, blank=True, related_name="blog_posts", verbose_name="Author")
    category = models.ForeignKey(BlogCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="posts", verbose_name="Category")
    tags = models.ManyToManyField(BlogTag, blank=True, related_name="posts", verbose_name="Tags")
    cover_image = models.ImageField(upload_to="blog/cover/", blank=True, null=True, verbose_name="Cover image")
    excerpt = HTMLField(blank=True, verbose_name="Excerpt")
    content = HTMLField(verbose_name="Content (Markdown/HTML)")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, verbose_name="Status")
    is_featured = models.BooleanField(default=False, verbose_name="Featured")
    allow_comments = models.BooleanField(default=True, verbose_name="Allow comments")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Published at")
    read_time_min = models.PositiveIntegerField(default=3, verbose_name="Estimated read (min)")
    views = models.PositiveIntegerField(default=0, verbose_name="Views")
    seo_title = models.CharField(max_length=180, blank=True, verbose_name="SEO title")
    seo_description = models.CharField(max_length=240, blank=True, verbose_name="SEO description")
    seo_keywords = models.CharField(max_length=240, blank=True, verbose_name="SEO keywords (comma-separated)")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Blog Post"
        verbose_name_plural = "Blog Posts"
        ordering = ("-published_at", "priority", "title")
        indexes = [models.Index(fields=["status", "published_at"]), models.Index(fields=["slug"])]

    def __str__(self):
        return self.title
class Notice(models.Model):
    title = models.CharField(max_length=180, verbose_name="Title")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    message = HTMLField(verbose_name="Message")
    link_url = models.URLField(blank=True, null=True, verbose_name="Link URL")
    attachment = models.FileField(upload_to="notices/files/", blank=True, null=True, verbose_name="Attachment")
    publish_start = models.DateTimeField(blank=True, null=True, verbose_name="Publish start")
    publish_end = models.DateTimeField(blank=True, null=True, verbose_name="Publish end")
    show_on_homepage = models.BooleanField(default=True, verbose_name="Show on homepage")
    popup_on_homepage = models.BooleanField(default=False, verbose_name="Show as popup on homepage")
    popup_until = models.DateTimeField(blank=True, null=True, verbose_name="Popup until")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Notice"
        verbose_name_plural = "Notices"
        ordering = ("priority", "-publish_start", "title")
        indexes = [
            models.Index(fields=["active", "publish_start", "publish_end"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title


class Gallery(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Gallery name")
    slug = models.SlugField(max_length=170, unique=True, verbose_name="Slug")
    description = HTMLField(blank=True, verbose_name="Description")
    cover_image = models.ImageField(upload_to="gallery/covers/", blank=True, null=True, verbose_name="Cover image")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Gallery"
        verbose_name_plural = "Galleries"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class GalleryPic(models.Model):
    gallery = models.ForeignKey(Gallery, on_delete=models.CASCADE, related_name="pictures", verbose_name="Gallery")
    title = models.CharField(max_length=160, verbose_name="Title")
    caption = models.CharField(max_length=240, blank=True, verbose_name="Caption")
    image = models.ImageField(upload_to="gallery/pictures/", verbose_name="Image")
    alt_text = models.CharField(max_length=160, blank=True, verbose_name="Alt text")
    photographer = models.CharField(max_length=120, blank=True, verbose_name="Photographer")
    taken_at = models.DateField(blank=True, null=True, verbose_name="Taken at")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Uploaded at")

    class Meta:
        verbose_name = "Gallery Picture"
        verbose_name_plural = "Gallery Pictures"
        ordering = ("gallery__name", "priority", "title")
        indexes = [models.Index(fields=["gallery", "priority"])]

    def __str__(self):
        return f"{self.title} ({self.gallery.name})"


class VideoAlbum(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Album name")
    slug = models.SlugField(max_length=170, unique=True, verbose_name="Slug")
    description = HTMLField(blank=True, verbose_name="Description")
    cover_image = models.ImageField(upload_to="video_albums/covers/", blank=True, null=True, verbose_name="Cover image")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Video Album"
        verbose_name_plural = "Video Albums"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class Video(models.Model):
    PROVIDERS = (
        ("youtube", "YouTube"),
        ("vimeo", "Vimeo"),
        ("other", "Other"),
    )
    album = models.ForeignKey(VideoAlbum, on_delete=models.CASCADE, related_name="videos", verbose_name="Album")
    title = models.CharField(max_length=160, verbose_name="Title")
    slug = models.SlugField(max_length=180, verbose_name="Slug", help_text="Optional", blank=True)
    video_url = models.URLField(verbose_name="Video URL")
    provider = models.CharField(max_length=12, choices=PROVIDERS, default="youtube", verbose_name="Provider")
    thumbnail = models.ImageField(upload_to="video_albums/thumbnails/", blank=True, null=True, verbose_name="Thumbnail")
    duration_seconds = models.PositiveIntegerField(default=0, verbose_name="Duration (sec)")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Published at")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")

    class Meta:
        verbose_name = "Video"
        verbose_name_plural = "Videos"
        ordering = ("album__name", "priority", "title")
        indexes = [models.Index(fields=["album", "priority"])]

    def __str__(self):
        return f"{self.title} ({self.album.name})"


class LatestNews(models.Model):
    class Status(models.TextChoices):
        DRAFT = "draft", "Draft"
        PUBLISHED = "published", "Published"
        ARCHIVED = "archived", "Archived"

    title = models.CharField(max_length=180, verbose_name="Title")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    subtitle = models.CharField(max_length=220, blank=True, verbose_name="Subtitle")
    image = models.ImageField(upload_to="news/images/", blank=True, null=True, verbose_name="Image")
    summary = models.CharField(max_length=300, blank=True, verbose_name="Summary")
    content = HTMLField(verbose_name="Content")
    source_url = models.URLField(blank=True, null=True, verbose_name="Source URL")
    author = models.ForeignKey(getattr(settings, "AUTH_USER_MODEL", "auth.User"), on_delete=models.SET_NULL, null=True, blank=True, related_name="news_items", verbose_name="Author")
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.DRAFT, verbose_name="Status")
    is_breaking = models.BooleanField(default=False, verbose_name="Breaking")
    show_on_homepage = models.BooleanField(default=True, verbose_name="Show on homepage")
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="Published at")
    views = models.PositiveIntegerField(default=0, verbose_name="Views")
    active = models.BooleanField(default=True, verbose_name="Active")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Latest News"
        verbose_name_plural = "Latest News"
        ordering = ("-published_at", "priority", "title")
        indexes = [
            models.Index(fields=["status", "published_at"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title


class ContactSubmission(models.Model):
    class Status(models.TextChoices):
        NEW = "new", "New"
        IN_PROGRESS = "in_progress", "In Progress"
        RESOLVED = "resolved", "Resolved"
        SPAM = "spam", "Spam"

    name = models.CharField(max_length=150, verbose_name="Name")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=40, blank=True, verbose_name="Phone")
    subject = models.CharField(max_length=180, verbose_name="Subject")
    message = HTMLField(verbose_name="Message")
    attachment = models.FileField(upload_to="contacts/attachments/", blank=True, null=True, verbose_name="Attachment")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.NEW, verbose_name="Status")
    is_read = models.BooleanField(default=False, verbose_name="Read")
    assigned_to = models.ForeignKey(getattr(settings, "AUTH_USER_MODEL", "auth.User"), on_delete=models.SET_NULL, null=True, blank=True, related_name="assigned_contacts", verbose_name="Assigned to")
    internal_notes = HTMLField(blank=True, verbose_name="Internal notes")
    ip_address = models.GenericIPAddressField(blank=True, null=True, verbose_name="IP address")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated at")

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ("-created_at", "status")
        indexes = [
            models.Index(fields=["status", "is_read"]),
            models.Index(fields=["email"]),
        ]

    def __str__(self):
        return f"{self.name} — {self.subject}"


class Settings(models.Model):
    logo = models.ImageField(upload_to="settings/logo/", blank=True, null=True, verbose_name="Logo")
    org_name = models.CharField(max_length=60, blank=True, verbose_name="Organization Name")
    phone1 = models.CharField(max_length=30, blank=True, verbose_name="Primary phone")
    phone2 = models.CharField(max_length=30, blank=True, verbose_name="Secondary phone")
    email1 = models.CharField(max_length=30, blank=True, verbose_name="Primary Email", default="info@hopehospital.com.np")
    email2 = models.CharField(max_length=30, blank=True, verbose_name="Secondary Email", default="info@hopehospital.com.np")
    address = models.TextField(blank=True, verbose_name="Address")
    map_link = models.CharField(blank=True, null=True, verbose_name="Google Map link <iframe>", max_length=1000)
    fb_link = models.URLField(blank=True, null=True, verbose_name="Facebook link")
    linkedin_link = models.URLField(blank=True, null=True, verbose_name="LinkedIn link")
    youtube_link = models.URLField(blank=True, null=True, verbose_name="YouTube link")
    insta_link = models.URLField(blank=True, null=True, verbose_name="Instagram link")

    class Meta:
        verbose_name = "Settings"
        verbose_name_plural = "Settings"

    def clean(self):
        if not self.pk and Settings.objects.exists():
            raise ValidationError("Only one Settings record is allowed.")

    def __str__(self):
        return "Site Settings"


class Service(models.Model):
    name = models.CharField(max_length=150, unique=True, verbose_name="Service name")
    icon = models.ImageField(upload_to="services/icon/", blank=True, null=True, verbose_name="Logo")
    slug = models.SlugField(max_length=170, unique=True, verbose_name="Slug")
    pic = models.ImageField(upload_to="services/images/", blank=True, null=True, verbose_name="Picture")
    desc = HTMLField(verbose_name="Description")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Service"
        verbose_name_plural = "Services"
        ordering = ("priority", "name")

    def __str__(self):
        return self.name


class Content(models.Model):
    code = models.CharField(max_length=80, unique=True, verbose_name="Code")
    name = models.CharField(max_length=150, verbose_name="Name")
    title = models.CharField(max_length=180, verbose_name="Title")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="Slug")
    image = models.ImageField(upload_to="content/images/", blank=True, null=True, verbose_name="Image")
    content = HTMLField(verbose_name="Content (HTML)", help_text="HTML allowed")
    parent = models.ForeignKey("self", on_delete=models.SET_NULL, null=True, blank=True, related_name="children", verbose_name="Parent")
    priority = models.IntegerField(default=0, verbose_name="Priority", help_text="Lower number appears first")

    class Meta:
        verbose_name = "Content"
        verbose_name_plural = "Contents"
        ordering = ("priority", "title")
        indexes = [
            models.Index(fields=["code"]),
            models.Index(fields=["slug"]),
        ]

    def __str__(self):
        return self.title

from django.db import models
from django.core.exceptions import ValidationError

class WebsiteContent(models.Model):
    # Slides
    slide1_text = models.CharField(max_length=255, default="Welcome to Slide 1")
    slide2_text = models.CharField(max_length=255, default="Welcome to Slide 2")
    slide3_text = models.CharField(max_length=255, default="Welcome to Slide 3")

    slide1_image = models.ImageField(upload_to="slides/", blank=True, null=True)
    slide2_image = models.ImageField(upload_to="slides/", blank=True, null=True)
    slide3_image = models.ImageField(upload_to="slides/", blank=True, null=True)

    slide1_desc = HTMLField(default="Slide 1 description here...")
    slide2_desc = HTMLField(default="Slide 2 description here...")
    slide3_desc = HTMLField(default="Slide 3 description here...")

    # Managing Director
    md_message = HTMLField(default="Message from the Managing Director...")
    md_pic = models.ImageField(upload_to="directors/", blank=True, null=True)

    # Chairman
    chairman_message = HTMLField(default="Message from the Chairman...")
    chairman_pic = models.ImageField(upload_to="chairman/", blank=True, null=True)

    class Meta:
        verbose_name = "Website Content"
        verbose_name_plural = "Website Content"

    def save(self, *args, **kwargs):
        """Ensure only one record exists."""
        if not self.pk and WebsiteContent.objects.exists():
            raise ValidationError("Only one WebsiteContent instance is allowed.")
        super().save(*args, **kwargs)

    def __str__(self):
        return "Website Content"
