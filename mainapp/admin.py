# admin.py
from django.utils.html import format_html
from django.contrib import admin
from django.db import models  # <-- needed for formfield_overrides
from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline, StackedInline
from .models import *
from unfold.contrib.forms.widgets import ArrayWidget, WysiwygWidget


# ------------------------
# Inlines
# ------------------------
class DepartmentServiceInline(TabularInline):
    model = DepartmentService
    extra = 1
    fields = ("name", "slug", "active", "priority")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


class DoctorInline(StackedInline):
    model = Doctor
    extra = 1
    fields = ("name", "slug", "image", "description", "active", "priority")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# ------------------------
# Admins
# ------------------------
@admin.register(Department)
class DepartmentAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "icon_preview", "active", "priority")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (DepartmentServiceInline, DoctorInline)
    fieldsets = (
        (None, {"fields": ("name", "slug", "active", "priority")}),
        ("Media & Description", {"fields": ("icon", "description")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:28px;width:28px;object-fit:cover;border-radius:6px;" />',
            obj.icon.url,
        ) if obj.icon else "—"


@admin.register(DepartmentService)
class DepartmentServiceAdmin(UnfoldModelAdmin):
    list_display = ("name", "department", "slug", "active", "priority")
    list_filter = ("active", "department")
    search_fields = ("name", "slug", "description", "department__name")
    list_editable = ("active", "priority")
    ordering = ("department__name", "priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("department",)
    fieldsets = (
        (None, {"fields": ("department", "name", "slug", "active", "priority")}),
        ("Details", {"fields": ("description",)}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Doctor)
class DoctorAdmin(UnfoldModelAdmin):
    list_display = ("name", "department", "slug", "active", "priority")
    list_filter = ("active", "department")
    search_fields = ("name", "slug", "description", "department__name")
    list_editable = ("active", "priority")
    ordering = ("department__name", "priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("department",)
    fieldsets = (
        (None, {"fields": ("name", "slug", "department", "active", "priority")}),
        ("Bio", {"fields": ("description",)}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(HealthPackage)
class HealthPackageAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "price", "image_preview", "active", "priority")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        (None, {"fields": ("name", "slug", "price", "active", "priority")}),
        ("Media & Description", {"fields": ("image", "description")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Image")
    def image_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:28px;width:28px;object-fit:cover;border-radius:6px;" />',
            obj.image.url,
        ) if obj.image else "—"


class TeamMemberInline(TabularInline):
    model = TeamMember
    extra = 1
    fields = ("name", "slug", "designation", "pic", "active", "priority")
    prepopulated_fields = {"slug": ("name",)}
    show_change_link = True


@admin.register(TeamDepartment)
class TeamDepartmentAdmin(UnfoldModelAdmin):
    list_display = ("name", "icon_preview", "active", "priority")
    list_filter = ("active",)
    search_fields = ("name", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    inlines = (TeamMemberInline,)
    fieldsets = (
        (None, {"fields": ("name", "active", "priority")}),
        ("Details", {"fields": ("description", "icon")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Icon")
    def icon_preview(self, obj):
        return format_html(
            '<img src="{}" style="height:28px;width:28px;object-fit:cover;border-radius:6px;" />',
            obj.icon.url,
        ) if obj.icon else "—"


# Helpers
def img_preview(obj, field_name, size=36):
    f = getattr(obj, field_name, None)
    return format_html(
        '<img src="{}" style="height:{}px;width:{}px;object-fit:cover;border-radius:6px;" />',
        f.url, size, size
    ) if f else "—"


# -------- Video Gallery --------
class VideoInline(TabularInline):
    model = Video
    extra = 1
    fields = ("title", "slug", "video_url", "provider", "thumbnail", "duration_seconds", "published_at", "active", "priority")
    show_change_link = True
    prepopulated_fields = {"slug": ("title",)}


@admin.register(VideoAlbum)
class VideoAlbumAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "cover_thumb", "active", "priority", "created_at")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (VideoInline,)
    fieldsets = (
        ("Main", {"fields": ("name", "slug", "active", "priority")}),
        ("Media & Description", {"fields": ("cover_image", "description")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Cover")
    def cover_thumb(self, obj): return img_preview(obj, "cover_image")


@admin.register(Video)
class VideoAdmin(UnfoldModelAdmin):
    list_display = ("title", "album", "provider", "video_url", "thumb", "active", "priority", "published_at", "created_at")
    list_filter = ("active", "provider", "album")
    search_fields = ("title", "slug", "video_url", "album__name")
    list_editable = ("active", "priority")
    ordering = ("album__name", "priority", "title")
    autocomplete_fields = ("album",)
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        ("Main", {"fields": ("album", "title", "slug", "provider", "video_url", "active", "priority")}),
        ("Media & Meta", {"fields": ("thumbnail", "duration_seconds", "published_at")}),
    )
    # (no text fields here that need WYSIWYG)
    @admin.display(description="Thumb")
    def thumb(self, obj): return img_preview(obj, "thumbnail")


# -------- Latest News --------
@admin.register(LatestNews)
class LatestNewsAdmin(UnfoldModelAdmin):
    list_display = ("title", "status", "is_breaking", "show_on_homepage", "published_at", "views", "priority", "img")
    list_filter = ("status", "is_breaking", "show_on_homepage", "active")
    search_fields = ("title", "subtitle", "slug", "summary", "content", "author__username", "author__first_name", "author__last_name")
    list_editable = ("is_breaking", "show_on_homepage", "priority")
    ordering = ("-published_at", "priority", "title")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author",)
    readonly_fields = ("created_at", "updated_at", "views")
    date_hierarchy = "published_at"
    fieldsets = (
        ("Main", {"fields": ("title", "slug", "subtitle", "author", "status", "is_breaking", "show_on_homepage", "active", "priority")}),
        ("Content", {"fields": ("summary", "content")}),
        ("Media", {"fields": ("image",)}),
        ("Meta", {"fields": ("published_at", "views", "created_at", "updated_at", "source_url")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Image")
    def img(self, obj): return img_preview(obj, "image")


# -------- Contact Form --------
@admin.register(ContactSubmission)
class ContactSubmissionAdmin(UnfoldModelAdmin):
    list_display = ("created_at", "name", "email", "phone", "subject", "status", "is_read", "assigned_to")
    list_filter = ("status", "is_read", "assigned_to")
    search_fields = ("name", "email", "phone", "subject", "message")
    list_editable = ("status", "is_read", "assigned_to")
    ordering = ("-created_at",)
    autocomplete_fields = ("assigned_to",)
    readonly_fields = ("created_at", "updated_at", "ip_address")
    fieldsets = (
        ("From", {"fields": ("name", "email", "phone")}),
        ("Message", {"fields": ("subject", "message")}),
        ("Workflow", {"fields": ("status", "is_read", "assigned_to", "internal_notes")}),
        ("Meta", {"fields": ("ip_address", "created_at", "updated_at")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# -------- Team Member (standalone) --------
@admin.register(TeamMember)
class TeamMemberAdmin(UnfoldModelAdmin):
    list_display = ("name", "designation", "department", "slug", "pic_thumb", "active", "priority")
    list_filter = ("active", "department")
    search_fields = ("name", "designation", "slug", "description", "department__name")
    list_editable = ("active", "priority")
    ordering = ("department__name", "priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    autocomplete_fields = ("department",)
    fieldsets = (
        ("Main", {"fields": ("name", "slug", "designation", "department", "active", "priority")}),
        ("Media & Bio", {"fields": ("pic", "description")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Pic")
    def pic_thumb(self, obj):
        return img_preview(obj, "pic")


# -------- Blog: Categories & Tags --------
@admin.register(BlogCategory)
class BlogCategoryAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "active", "priority")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Main", {"fields": ("name", "slug", "active", "priority")}),
        ("Description", {"fields": ("description",)}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(BlogTag)
class BlogTagAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug")
    search_fields = ("name", "slug")
    ordering = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(BlogPost)
class BlogPostAdmin(UnfoldModelAdmin):
    list_display = ("title", "status", "is_featured", "category", "author", "published_at", "views", "priority")
    list_filter = ("status", "is_featured", "active", "category")
    search_fields = ("title", "slug", "subtitle", "excerpt", "content", "seo_title", "seo_description", "seo_keywords", "author__username", "author__first_name", "author__last_name")
    list_editable = ("is_featured", "priority")
    ordering = ("-published_at", "priority", "title")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("author", "category")
    filter_horizontal = ("tags",)
    readonly_fields = ("created_at", "updated_at", "views")
    date_hierarchy = "published_at"
    fieldsets = (
        ("Main", {"fields": ("title", "slug", "subtitle", "author", "category", "tags", "status", "is_featured", "active", "priority")}),
        ("Content", {"fields": ("excerpt", "content")}),
        ("Media", {"fields": ("cover_image",)}),
        ("SEO", {"fields": ("seo_title", "seo_description", "seo_keywords")}),
        ("Meta", {"fields": ("published_at", "views", "created_at", "updated_at")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# -------- Notices --------
@admin.register(Notice)
class NoticeAdmin(UnfoldModelAdmin):
    list_display = ("title", "show_on_homepage", "popup_on_homepage", "popup_until", "publish_start", "publish_end", "active", "priority")
    list_filter = ("active", "show_on_homepage", "popup_on_homepage")
    search_fields = ("title", "slug", "message")
    list_editable = ("show_on_homepage", "popup_on_homepage", "priority", "active")
    ordering = ("priority", "-publish_start", "title")
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "publish_start"
    fieldsets = (
        ("Main", {"fields": ("title", "slug", "message", "active", "priority")}),
        ("Links & Files", {"fields": ("link_url", "attachment")}),
        ("Publishing", {"fields": ("publish_start", "publish_end", "show_on_homepage", "popup_on_homepage", "popup_until")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# -------- Gallery & Pictures --------
class GalleryPicInline(TabularInline):
    model = GalleryPic
    extra = 1
    fields = ("title", "caption", "image", "alt_text", "photographer", "taken_at", "active", "priority")
    show_change_link = True


@admin.register(Gallery)
class GalleryAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "cover_thumb", "active", "priority", "created_at")
    list_filter = ("active",)
    search_fields = ("name", "slug", "description")
    list_editable = ("active", "priority")
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    inlines = (GalleryPicInline,)
    fieldsets = (
        ("Main", {"fields": ("name", "slug", "active", "priority")}),
        ("Media & Description", {"fields": ("cover_image", "description")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        return img_preview(obj, "cover_image")


@admin.register(GalleryPic)
class GalleryPicAdmin(UnfoldModelAdmin):
    list_display = ("title", "gallery", "img", "photographer", "taken_at", "active", "priority", "created_at")
    list_filter = ("active", "gallery")
    search_fields = ("title", "caption", "gallery__name", "photographer", "alt_text")
    list_editable = ("active", "priority")
    ordering = ("gallery__name", "priority", "title")
    autocomplete_fields = ("gallery",)
    fieldsets = (
        ("Main", {"fields": ("gallery", "title", "caption", "image", "alt_text", "active", "priority")}),
        ("Meta", {"fields": ("photographer", "taken_at")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Image")
    def img(self, obj):
        return img_preview(obj, "image")


# -------- Services --------
@admin.register(Service)
class ServiceAdmin(UnfoldModelAdmin):
    list_display = ("name", "slug", "pic_thumb", "priority")
    search_fields = ("name", "slug", "desc")
    list_editable = ("priority",)
    ordering = ("priority", "name")
    prepopulated_fields = {"slug": ("name",)}
    fieldsets = (
        ("Main", {"fields": ("name", "slug", "priority")}),
        ("Media & Description", {"fields": ("pic", "desc", "icon")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    @admin.display(description="Pic")
    def pic_thumb(self, obj):
        return img_preview(obj, "pic")


# -------- Content (Hierarchical) --------
@admin.register(Content)
class ContentAdmin(UnfoldModelAdmin):
    list_display = ("code", "name", "title", "parent", "slug", "priority")
    list_filter = ("parent",)
    search_fields = ("code", "name", "title", "slug", "content")
    list_editable = ("priority",)
    ordering = ("priority", "title")
    prepopulated_fields = {"slug": ("title",)}
    autocomplete_fields = ("parent",)
    fieldsets = (
        ("Main", {"fields": ("code", "name", "title", "slug", "parent", "priority")}),
        ("Media & Body", {"fields": ("image", "content")}),
    )
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# -------- Settings (Singleton) --------
@admin.register(Settings)
class SettingsAdmin(UnfoldModelAdmin):
    list_display = ("__str__", "logo_thumb", "phone1", "phone2")
    search_fields = ("phone1", "phone2", "address")
    fieldsets = (
        ("Brand", {"fields": ("logo",)}),
        ("Contact", {"fields": ("phone1", "phone2", "address", "map_link")}),
        ("Social", {"fields": ("fb_link", "linkedin_link", "youtube_link", "insta_link")}),
    )
     

    @admin.display(description="Logo")
    def logo_thumb(self, obj):
        return img_preview(obj, "logo")

    # Enforce single record in admin UI
    def has_add_permission(self, request):
        # allow add only if no Settings instance exists
        return not Settings.objects.exists() or super().has_add_permission(request)


from django.contrib import admin
from unfold.admin import ModelAdmin as UnfoldModelAdmin
from .models import WebsiteContent


@admin.register(WebsiteContent)
class WebsiteContentAdmin(UnfoldModelAdmin):
    list_display = ("__str__",)

    fieldsets = (
        ("Slides", {
            "fields": (
                "slide1_text", "slide1_image", "slide1_desc",
                "slide2_text", "slide2_image", "slide2_desc",
                "slide3_text", "slide3_image", "slide3_desc",
            ),
            "description": "Manage homepage slide texts, images, and descriptions."
        }),
        ("Managing Director", {
            "fields": ("md_message", "md_pic"),
            "description": "Content for the Managing Director's section."
        }),
        ("Chairman", {
            "fields": ("chairman_message", "chairman_pic"),
            "description": "Content for the Chairman's section."
        }),
    )

    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    def has_add_permission(self, request):
        """Allow adding only if no record exists."""
        return not WebsiteContent.objects.exists()

    def has_delete_permission(self, request, obj=None):
        """Disable deletion of the singleton instance."""
        return False
