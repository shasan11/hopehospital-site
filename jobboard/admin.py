# jobboard/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from unfold.admin import ModelAdmin as UnfoldModelAdmin, TabularInline, StackedInline
from unfold.contrib.forms.widgets import WysiwygWidget

from django.db import models

from .models import (
    Department, Location, Specialty, Credential,
    JobPosting, ScreeningQuestion,
    Candidate, CandidateExperience, CandidateEducation, CandidateCertification, CandidateReference,
    Application, ApplicationAnswer, ApplicationStatusHistory,
    Interview, InterviewFeedback,
    Offer, OnboardingTask,
    Attachment, ActivityLog,
    EmploymentType, ShiftType, JobStatus, ApplicationStage, OfferStatus
)

# ------------- Inlines -------------

class ScreeningQuestionInline(TabularInline):
    model = ScreeningQuestion
    extra = 0
    fields = ("question", "question_type", "required", "active")
    show_change_link = True


class CandidateExperienceInline(StackedInline):
    model = CandidateExperience
    extra = 0
    fields = ("organization", "role", "start_date", "end_date", "is_current", "description")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class CandidateEducationInline(StackedInline):
    model = CandidateEducation
    extra = 0
    fields = ("institution", "degree", "field_of_study", "start_year", "end_year", "grade_gpa", "description")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class CandidateCertificationInline(TabularInline):
    model = CandidateCertification
    extra = 0
    fields = ("credential", "license_no", "issued_on", "expires_on")


class CandidateReferenceInline(TabularInline):
    model = CandidateReference
    extra = 0
    fields = ("name", "relationship", "email", "phone", "notes")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class ApplicationAnswerInline(StackedInline):
    model = ApplicationAnswer
    extra = 0
    fields = ("question", "answer_text", "answer_bool", "answer_number", "answer_choices")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class InterviewInline(TabularInline):
    model = Interview
    extra = 0
    fields = ("interview_type", "scheduled_at", "duration_minutes", "location_text", "meeting_url", "panel")
    filter_horizontal = ("panel",)


class InterviewFeedbackInline(TabularInline):
    model = InterviewFeedback
    extra = 0
    fields = ("reviewer", "rating", "recommendation", "comments")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


class OnboardingTaskInline(TabularInline):
    model = OnboardingTask
    extra = 0
    fields = ("title", "description", "due_days_after_accept", "is_completed", "assigned_to_department")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


# ------------- Admins -------------

@admin.register(Department)
class DepartmentAdmin(UnfoldModelAdmin):
    list_display = ("name", "priority", "active")
    list_editable = ("priority", "active",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Location)
class LocationAdmin(UnfoldModelAdmin):
    list_display = ("name", "city", "country", "active")
    list_filter = ("country", "active")
    search_fields = ("name", "city", "state", "country")
    prepopulated_fields = {"slug": ("name", "city", "country")}


@admin.register(Specialty)
class SpecialtyAdmin(UnfoldModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Credential)
class CredentialAdmin(UnfoldModelAdmin):
    list_display = ("code", "name", "issuer", "country")
    list_filter = ("country", "issuer")
    search_fields = ("code", "name", "issuer")


@admin.register(JobPosting)
class JobPostingAdmin(UnfoldModelAdmin):
    list_display = (
        "reference", "title", "department", "location", "employment_type",
        "status", "publish_at", "application_deadline",
        "openings", "hired_count_display", "total_apps_display",
    )
    list_filter = (
        "status", "department", "location", "employment_type", "shift",
    )
    search_fields = ("reference", "title", "seo_title", "tags")
    date_hierarchy = "publish_at"
    inlines = [ScreeningQuestionInline]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("reference", "hired_count_display", "total_apps_display", "created_at", "updated_at")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},  # description/responsibilities/requirements/benefits
    }

    fieldsets = (
        ("Identity", {
            "fields": ("reference", "title", "slug", "department", "specialties", "credentials_required", "location")
        }),
        ("Employment", {
            "fields": ("employment_type", "shift", "grade_band", "openings",
                       "experience_min_years", "experience_max_years",
                       "salary_min", "salary_max", "salary_type", "currency",
                       "remote_allowed"),
        }),
        ("Publication", {
            "fields": ("status", "publish_at", "application_deadline", "posted_by"),
        }),
        ("Content", {
            "fields": ("short_description", "description", "responsibilities", "requirements", "benefits"),
        }),
        ("Apply", {
            "fields": ("apply_email", "external_apply_url"),
        }),
        ("SEO", {
            "fields": ("seo_title", "seo_description", "tags"),
        }),
        ("Stats", {
            "fields": ("hired_count_display", "total_apps_display", "created_at", "updated_at"),
        }),
    )

    filter_horizontal = ("specialties", "credentials_required")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("department", "location", "posted_by")

    @admin.display(description="Hired", ordering=None)
    def hired_count_display(self, obj):
        return obj.hired_count

    @admin.display(description="Applications", ordering=None)
    def total_apps_display(self, obj):
        return obj.total_applications

    # Quick actions
    @admin.action(description="Mark selected jobs OPEN now")
    def make_open(self, request, queryset):
        updated = queryset.update(status=JobStatus.OPEN, publish_at=timezone.now())
        self.message_user(request, f"{updated} job(s) marked OPEN.")

    @admin.action(description="Close selected jobs")
    def make_closed(self, request, queryset):
        updated = queryset.update(status=JobStatus.CLOSED)
        self.message_user(request, f"{updated} job(s) closed.")

    actions = ["make_open", "make_closed"]


@admin.register(ScreeningQuestion)
class ScreeningQuestionAdmin(UnfoldModelAdmin):
    list_display = ("question", "question_type", "required", "active", "job")
    list_filter = ("question_type", "required", "active")
    search_fields = ("question",)
    autocomplete_fields = ("job",)


@admin.register(Candidate)
class CandidateAdmin(UnfoldModelAdmin):
    list_display = ("full_name", "email", "phone", "user", "created_at")
    search_fields = ("full_name", "email", "phone")
    list_filter = ("data_processing_consent",)
    inlines = [CandidateExperienceInline, CandidateEducationInline, CandidateCertificationInline, CandidateReferenceInline]
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Application)
class ApplicationAdmin(UnfoldModelAdmin):
    list_display = ("candidate", "job", "stage", "applied_at", "current_score")
    list_filter = ("stage", "status", "job__department", "job__location")
    search_fields = ("candidate__full_name", "candidate__email", "job__reference", "job__title")
    date_hierarchy = "applied_at"
    autocomplete_fields = ("job", "candidate")
    inlines = [ApplicationAnswerInline, InterviewInline, OnboardingTaskInline]
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.select_related("job", "candidate")


@admin.register(ApplicationStatusHistory)
class ApplicationStatusHistoryAdmin(UnfoldModelAdmin):
    list_display = ("application", "from_stage", "to_stage", "changed_by", "created_at")
    list_filter = ("from_stage", "to_stage")
    search_fields = ("application__candidate__full_name", "application__job__reference", "changed_by__username")
    autocomplete_fields = ("application", "changed_by")


@admin.register(Interview)
class InterviewAdmin(UnfoldModelAdmin):
    list_display = ("application", "interview_type", "scheduled_at", "duration_minutes")
    list_filter = ("interview_type",)
    search_fields = ("application__candidate__full_name", "application__job__reference")
    autocomplete_fields = ("application",)
    filter_horizontal = ("panel",)


@admin.register(InterviewFeedback)
class InterviewFeedbackAdmin(UnfoldModelAdmin):
    list_display = ("interview", "reviewer", "rating", "recommendation", "created_at")
    list_filter = ("rating", "recommendation")
    search_fields = ("interview__application__candidate__full_name", "reviewer__username")
    autocomplete_fields = ("interview", "reviewer")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Offer)
class OfferAdmin(UnfoldModelAdmin):
    list_display = ("application", "status", "base_salary", "currency", "sent_at", "accepted_at")
    list_filter = ("status", "currency")
    search_fields = ("application__candidate__full_name", "application__job__reference")
    autocomplete_fields = ("application",)
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(OnboardingTask)
class OnboardingTaskAdmin(UnfoldModelAdmin):
    list_display = ("title", "application", "assigned_to_department", "is_completed", "due_days_after_accept")
    list_filter = ("is_completed", "assigned_to_department")
    search_fields = ("title", "application__candidate__full_name", "application__job__reference")
    autocomplete_fields = ("application", "assigned_to_department")
    formfield_overrides = {
        models.TextField: {"widget": WysiwygWidget},
    }


@admin.register(Attachment)
class AttachmentAdmin(UnfoldModelAdmin):
    list_display = ("content_type", "object_id", "uploaded_by", "caption", "created_at")
    search_fields = ("caption",)
    list_filter = ("content_type",)
    autocomplete_fields = ("uploaded_by",)


@admin.register(ActivityLog)
class ActivityLogAdmin(UnfoldModelAdmin):
    list_display = ("verb", "actor", "content_type", "object_id", "created_at")
    list_filter = ("verb", "content_type")
    search_fields = ("verb", "actor__username")
    readonly_fields = ("actor", "verb", "content_type", "object_id", "notes", "created_at", "updated_at")
