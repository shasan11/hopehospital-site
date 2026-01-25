# jobs/models.py
from django.db import models
from django.contrib.auth import get_user_model
from django.utils.text import slugify
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models import Q, F
from django.db.models.functions import Coalesce

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()

# ----------------------------
# Base / Utilities
# ----------------------------
class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="created at")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="updated at")

    class Meta:
        abstract = True


def upload_resume(instance, filename):
    # Works for Candidate and Application.resume_snapshot
    cid = getattr(instance, "candidate_id", None)
    if not cid and hasattr(instance, "application") and instance.application_id:
        cid = instance.application.candidate_id
    return f"careers/candidates/{cid or 'unknown'}/resumes/{filename}"


def upload_attachment(instance, filename):
    return f"careers/attachments/{instance.pk or 'new'}/{filename}"


def upload_offer(instance, filename):
    return f"careers/offers/{instance.application_id}/{filename}"


# A simple reference code generator: JOB-YYYY-XXXX
def next_job_ref():
    prefix = f"JOB-{timezone.now().year}-"
    last = JobPosting.objects.filter(reference__startswith=prefix).order_by("-id").first()
    if not last:
        return f"{prefix}0001"
    try:
        num = int(last.reference.split("-")[-1])
    except Exception:
        num = 0
    return f"{prefix}{num+1:04d}"


# ----------------------------
# Master Data
# ----------------------------
class Department(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True, verbose_name="department name")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="slug")
    icon = models.ImageField(upload_to="careers/departments/icons/", blank=True, null=True, verbose_name="icon")
    description = models.TextField(blank=True, verbose_name="description")
    active = models.BooleanField(default=True, verbose_name="is active")
    priority = models.PositiveIntegerField(default=100, verbose_name="priority")

    class Meta:
        verbose_name = "Department"
        verbose_name_plural = "Departments"
        ordering = ["priority", "name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args, **kwargs)


class Location(TimeStampedModel):
    name = models.CharField(max_length=150, verbose_name="location name")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="slug")
    address = models.TextField(blank=True, verbose_name="address")
    city = models.CharField(max_length=100, blank=True, verbose_name="city")
    state = models.CharField(max_length=100, blank=True, verbose_name="state/region")
    country = models.CharField(max_length=100, default="Nepal", verbose_name="country")
    postal_code = models.CharField(max_length=20, blank=True, verbose_name="postal code")
    active = models.BooleanField(default=True, verbose_name="is active")

    class Meta:
        verbose_name = "Location"
        verbose_name_plural = "Locations"
        unique_together = [("name", "city", "country")]

    def __str__(self):
        return f"{self.name} ({self.city or self.country})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.name}-{self.city or ''}-{self.country}".strip()
            self.slug = slugify(base)[:160]
        super().save(*args, **kwargs)


class Specialty(TimeStampedModel):
    name = models.CharField(max_length=150, unique=True, verbose_name="specialty")
    slug = models.SlugField(max_length=160, unique=True, verbose_name="slug")

    class Meta:
        verbose_name = "Specialty"
        verbose_name_plural = "Specialties"
        ordering = ["name"]

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)[:160]
        super().save(*args, **kwargs)


class Credential(TimeStampedModel):
    """Licenses/registrations required, eg. NMC (Nepal Nursing Council), etc."""
    code = models.CharField(max_length=50, verbose_name="credential code")
    name = models.CharField(max_length=150, verbose_name="credential name")
    issuer = models.CharField(max_length=150, blank=True, verbose_name="issuer")
    country = models.CharField(max_length=100, blank=True, verbose_name="country")

    class Meta:
        verbose_name = "Credential / License"
        verbose_name_plural = "Credentials / Licenses"
        unique_together = [("code", "issuer")]

    def __str__(self):
        return f"{self.code} – {self.name}"


# ----------------------------
# Enumerations
# ----------------------------
class EmploymentType(models.TextChoices):
    FULL_TIME = "FULL_TIME", "Full-time"
    PART_TIME = "PART_TIME", "Part-time"
    CONTRACT = "CONTRACT", "Contract"
    LOCUM = "LOCUM", "Locum"
    INTERNSHIP = "INTERNSHIP", "Internship"
    TEMPORARY = "TEMPORARY", "Temporary"
    VOLUNTEER = "VOLUNTEER", "Volunteer"


class ShiftType(models.TextChoices):
    DAY = "DAY", "Day Shift"
    NIGHT = "NIGHT", "Night Shift"
    ROTATIONAL = "ROTATIONAL", "Rotational"
    FLEX = "FLEX", "Flexible"


class JobStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    OPEN = "OPEN", "Open"
    PAUSED = "PAUSED", "Paused"
    CLOSED = "CLOSED", "Closed"
    FILLED = "FILLED", "Filled"


class ApplicationStage(models.TextChoices):
    APPLIED = "APPLIED", "Applied"
    SCREENING = "SCREENING", "Screening"
    ASSESSMENT = "ASSESSMENT", "Assessment"
    INTERVIEW = "INTERVIEW", "Interview"
    OFFER = "OFFER", "Offer"
    HIRED = "HIRED", "Hired"
    REJECTED = "REJECTED", "Rejected"
    WITHDRAWN = "WITHDRAWN", "Withdrawn"


class InterviewType(models.TextChoices):
    PHONE = "PHONE", "Phone"
    VIRTUAL = "VIRTUAL", "Virtual"
    ONSITE = "ONSITE", "Onsite"
    PANEL = "PANEL", "Panel"


class OfferStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SENT = "SENT", "Sent"
    ACCEPTED = "ACCEPTED", "Accepted"
    DECLINED = "DECLINED", "Declined"
    EXPIRED = "EXPIRED", "Expired"


class SalaryType(models.TextChoices):
    YEARLY = "YEARLY", "Yearly"
    MONTHLY = "MONTHLY", "Monthly"
    WEEKLY = "WEEKLY", "Weekly"
    DAILY = "DAILY", "Daily"
    HOURLY = "HOURLY", "Hourly"


# ----------------------------
# Custom QuerySets
# ----------------------------
class JobPostingQuerySet(models.QuerySet):
    def published(self):
        now = timezone.now()
        return self.filter(
            status=JobStatus.OPEN
        ).filter(Q(publish_at__isnull=True) | Q(publish_at__lte=now))

    def open_now(self):
        # open and not past deadline (or no deadline)
        today = timezone.localdate()
        return self.published().filter(
            Q(application_deadline__isnull=True) | Q(application_deadline__gte=today)
        )

    def featured(self):
        return self.filter(priority__lte=10)


# ----------------------------
# Job Posting
# ----------------------------
class JobPosting(TimeStampedModel):
    reference = models.CharField(max_length=20, unique=True, default=next_job_ref, verbose_name="job reference")
    title = models.CharField(max_length=200, verbose_name="title")
    slug = models.SlugField(max_length=220, unique=True, verbose_name="slug")
    department = models.ForeignKey('Department', on_delete=models.PROTECT, related_name="jobs", verbose_name="department")
    specialties = models.ManyToManyField('Specialty', blank=True, related_name="jobs", verbose_name="specialties")
    credentials_required = models.ManyToManyField('Credential', blank=True, related_name="jobs", verbose_name="required credentials")
    location = models.ForeignKey('Location', on_delete=models.PROTECT, related_name="jobs", verbose_name="location")
    employment_type = models.CharField(max_length=20, choices=EmploymentType.choices, default=EmploymentType.FULL_TIME, verbose_name="employment type")
    shift = models.CharField(max_length=20, choices=ShiftType.choices, default=ShiftType.DAY, verbose_name="shift")
    grade_band = models.CharField(max_length=50, blank=True, verbose_name="grade / band")
    openings = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)], verbose_name="number of openings")

    experience_min_years = models.PositiveIntegerField(default=0, verbose_name="minimum experience (years)")
    experience_max_years = models.PositiveIntegerField(default=0, verbose_name="maximum experience (years)")
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="min salary")
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True, verbose_name="max salary")
    salary_type = models.CharField(max_length=10, choices=SalaryType.choices, default=SalaryType.MONTHLY, verbose_name="salary type")
    currency = models.CharField(max_length=10, default="NPR", verbose_name="currency")

    remote_allowed = models.BooleanField(default=False, verbose_name="remote allowed")
    application_deadline = models.DateField(blank=True, null=True, verbose_name="application deadline")
    publish_at = models.DateTimeField(blank=True, null=True, verbose_name="publish at")
    status = models.CharField(max_length=10, choices=JobStatus.choices, default=JobStatus.DRAFT, verbose_name="status")

    # Content
    short_description = models.CharField(max_length=350, blank=True, verbose_name="short description")
    description = models.TextField(verbose_name="full description")
    responsibilities = models.TextField(blank=True, verbose_name="responsibilities")
    requirements = models.TextField(blank=True, verbose_name="requirements")
    benefits = models.TextField(blank=True, verbose_name="benefits")

    # Apply channels
    apply_email = models.EmailField(blank=True, verbose_name="apply email")
    external_apply_url = models.URLField(blank=True, verbose_name="external apply URL")

    # Meta / SEO
    seo_title = models.CharField(max_length=70, blank=True, verbose_name="SEO title")
    seo_description = models.CharField(max_length=160, blank=True, verbose_name="SEO description")
    tags = models.CharField(max_length=250, blank=True, verbose_name="tags (comma-separated)")

    posted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="posted_jobs", verbose_name="posted by")

    # Manager
    objects = JobPostingQuerySet.as_manager()

    class Meta:
        verbose_name = "Job Posting"
        verbose_name_plural = "Job Postings"
        indexes = [
            models.Index(fields=["status", "publish_at"]),
            models.Index(fields=["department", "location"]),
            models.Index(fields=["slug"]),
        ]
        ordering = ["-created_at"]
        constraints = [
            # salary_min <= salary_max (or either is null)
            models.CheckConstraint(
                check=Q(salary_min__isnull=True) | Q(salary_max__isnull=True) | Q(salary_min__lte=F("salary_max")),
                name="job_salary_min_lte_max_or_null",
            ),
            # experience_min <= experience_max (or max == 0 treated as "no upper limit")
            models.CheckConstraint(
                check=Q(experience_max_years=0) | Q(experience_min_years__lte=F("experience_max_years")),
                name="job_exp_min_lte_max_or_zero",
            ),
        ]

    def __str__(self):
        return f"{self.reference} – {self.title}"

    # ---------- Helpers ----------
    @property
    def is_published(self) -> bool:
        now = timezone.now()
        return self.status == JobStatus.OPEN and (self.publish_at is None or self.publish_at <= now)

    @property
    def is_open(self) -> bool:
        # Published and not expired and not filled/closed
        if self.status not in [JobStatus.OPEN, JobStatus.PAUSED]:
            return False
        if self.application_deadline and self.application_deadline < timezone.localdate():
            return False
        return True

    @property
    def hired_count(self) -> int:
        return self.applications.filter(stage=ApplicationStage.HIRED).count()

    @property
    def total_applications(self) -> int:
        return self.applications.count()

    def clean(self):
        from django.core.exceptions import ValidationError
        # At least one apply channel
        if not self.apply_email and not self.external_apply_url:
            raise ValidationError("Provide at least one apply channel (apply_email or external_apply_url).")

        # Experience clamp (already constrained, but give nice message)
        if self.experience_max_years and self.experience_min_years > self.experience_max_years != 0:
            raise ValidationError("Minimum experience cannot exceed maximum experience.")

        # Salary clamp friendly message
        if self.salary_min and self.salary_max and self.salary_min > self.salary_max:
            raise ValidationError("Minimum salary cannot exceed maximum salary.")

        # Deadline cannot be in the past (when opening)
        if self.status == JobStatus.OPEN and self.application_deadline and self.application_deadline < timezone.localdate():
            raise ValidationError("Application deadline cannot be in the past for OPEN jobs.")

    def save(self, *args, **kwargs):
        if not self.slug:
            base = f"{self.title}-{self.reference}"
            self.slug = slugify(base)[:220]
        # Clamp experience
        if self.experience_max_years and self.experience_min_years:
            self.experience_max_years = max(self.experience_max_years, self.experience_min_years)
        super().save(*args, **kwargs)

    def close_if_past_deadline(self):
        if self.application_deadline and self.application_deadline < timezone.localdate():
            if self.status == JobStatus.OPEN:
                self.status = JobStatus.CLOSED
                self.save(update_fields=["status", "updated_at"])

    def mark_filled_if_enough_hires(self):
        if self.status in [JobStatus.OPEN, JobStatus.PAUSED] and self.hired_count >= self.openings:
            self.status = JobStatus.FILLED
            self.save(update_fields=["status", "updated_at"])


# ----------------------------
# Screening Questions
# ----------------------------
class ScreeningQuestion(TimeStampedModel):
    class QuestionType(models.TextChoices):
        TEXT = "TEXT", "Text"
        BOOLEAN = "BOOLEAN", "Yes/No"
        SINGLE_CHOICE = "SINGLE", "Single Choice"
        MULTI_CHOICE = "MULTI", "Multiple Choice"
        NUMBER = "NUMBER", "Number"

    question = models.CharField(max_length=300, verbose_name="question")
    question_type = models.CharField(max_length=10, choices=QuestionType.choices, default=QuestionType.TEXT, verbose_name="type")
    options = models.JSONField(blank=True, null=True, verbose_name="options (for choice)")
    required = models.BooleanField(default=False, verbose_name="required")
    active = models.BooleanField(default=True, verbose_name="is active")

    # Scope: global library OR attached to a job
    job = models.ForeignKey(JobPosting, null=True, blank=True, on_delete=models.CASCADE, related_name="screening_questions", verbose_name="job")

    class Meta:
        verbose_name = "Screening Question"
        verbose_name_plural = "Screening Questions"

    def __str__(self):
        return self.question


# ----------------------------
# Candidate Profile
# ----------------------------
class Candidate(TimeStampedModel):
    full_name = models.CharField(max_length=150, verbose_name="full name")
    email = models.EmailField(verbose_name="email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="phone")
    linkedin = models.URLField(blank=True, verbose_name="LinkedIn")
    website = models.URLField(blank=True, verbose_name="website/portfolio")
    address = models.TextField(blank=True, verbose_name="address")
    user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name="candidate_profile", verbose_name="user (optional)")
    resume = models.FileField(upload_to=upload_resume, blank=True, null=True, verbose_name="primary resume")
    cover_letter = models.TextField(blank=True, verbose_name="cover letter")

    # Optional: EEO/GDPR flags (store consent only)
    data_processing_consent = models.BooleanField(default=False, verbose_name="GDPR consent")

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"
        indexes = [models.Index(fields=["email"])]

    def __str__(self):
        return f"{self.full_name} <{self.email}>"

    def anonymize(self):
        """
        GDPR helper: strip PII while keeping relational integrity.
        """
        masked_at = timezone.now().strftime("%Y%m%d%H%M%S")
        self.full_name = f"Candidate-{self.pk}-{masked_at}"
        self.email = f"candidate-{self.pk}-{masked_at}@masked.local"
        self.phone = ""
        self.linkedin = ""
        self.website = ""
        self.address = ""
        self.cover_letter = ""
        self.save()


class CandidateExperience(TimeStampedModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="experiences", verbose_name="candidate")
    organization = models.CharField(max_length=150, verbose_name="organization")
    role = models.CharField(max_length=150, verbose_name="role")
    start_date = models.DateField(verbose_name="start date")
    end_date = models.DateField(blank=True, null=True, verbose_name="end date")
    is_current = models.BooleanField(default=False, verbose_name="current role")
    description = models.TextField(blank=True, verbose_name="description")

    class Meta:
        verbose_name = "Candidate Experience"
        verbose_name_plural = "Candidate Experiences"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.role} @ {self.organization}"


class CandidateEducation(TimeStampedModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="education", verbose_name="candidate")
    institution = models.CharField(max_length=150, verbose_name="institution")
    degree = models.CharField(max_length=150, verbose_name="degree")
    field_of_study = models.CharField(max_length=150, blank=True, verbose_name="field of study")
    start_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="start year")
    end_year = models.PositiveIntegerField(blank=True, null=True, verbose_name="end year")
    grade_gpa = models.CharField(max_length=50, blank=True, verbose_name="grade/GPA")
    description = models.TextField(blank=True, verbose_name="description")

    class Meta:
        verbose_name = "Candidate Education"
        verbose_name_plural = "Candidate Education"
        ordering = ["-end_year", "-start_year"]

    def __str__(self):
        return f"{self.degree} – {self.institution}"


class CandidateCertification(TimeStampedModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="certifications", verbose_name="candidate")
    credential = models.ForeignKey(Credential, on_delete=models.PROTECT, related_name="candidate_certifications", verbose_name="credential/license")
    license_no = models.CharField(max_length=100, blank=True, verbose_name="license number")
    issued_on = models.DateField(blank=True, null=True, verbose_name="issued on")
    expires_on = models.DateField(blank=True, null=True, verbose_name="expires on")

    class Meta:
        verbose_name = "Candidate Certification"
        verbose_name_plural = "Candidate Certifications"

    def __str__(self):
        return f"{self.credential} – {self.license_no or 'n/a'}"


class CandidateReference(TimeStampedModel):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="references", verbose_name="candidate")
    name = models.CharField(max_length=150, verbose_name="name")
    relationship = models.CharField(max_length=100, blank=True, verbose_name="relationship")
    email = models.EmailField(blank=True, verbose_name="email")
    phone = models.CharField(max_length=50, blank=True, verbose_name="phone")
    notes = models.TextField(blank=True, verbose_name="notes")

    class Meta:
        verbose_name = "Candidate Reference"
        verbose_name_plural = "Candidate References"

    def __str__(self):
        return f"{self.name} – {self.relationship}"


# ----------------------------
# Applications
# ----------------------------
class Application(TimeStampedModel):
    job = models.ForeignKey(JobPosting, on_delete=models.CASCADE, related_name="applications", verbose_name="job")
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name="applications", verbose_name="candidate")
    source = models.CharField(max_length=100, blank=True, verbose_name="source (e.g., website, referral)")
    stage = models.CharField(max_length=15, choices=ApplicationStage.choices, default=ApplicationStage.APPLIED, verbose_name="stage")
    status = models.CharField(max_length=15, choices=ApplicationStage.choices, default=ApplicationStage.APPLIED, verbose_name="status (mirror of stage)")
    current_score = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="screening score")
    notes = models.TextField(blank=True, verbose_name="internal notes")
    applied_at = models.DateTimeField(default=timezone.now, verbose_name="applied at")
    resume_snapshot = models.FileField(upload_to=upload_resume, blank=True, null=True, verbose_name="resume snapshot (optional)")

    class Meta:
        verbose_name = "Application"
        verbose_name_plural = "Applications"
        unique_together = [("job", "candidate")]
        indexes = [models.Index(fields=["job", "stage"]), models.Index(fields=["candidate", "status"])]

    def __str__(self):
        return f"{self.candidate} → {self.job.reference}"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Keep stage and status aligned (UI can change one)
        if self.stage != self.status:
            # We'll sync in save, but warn here for admin clarity
            pass

    def save(self, *args, **kwargs):
        # Always mirror stage -> status to keep consistent
        if self.status != self.stage:
            self.status = self.stage
        super().save(*args, **kwargs)


class ApplicationAnswer(TimeStampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="answers", verbose_name="application")
    question = models.ForeignKey(ScreeningQuestion, on_delete=models.PROTECT, related_name="answers", verbose_name="question")
    answer_text = models.TextField(blank=True, verbose_name="text answer")
    answer_bool = models.BooleanField(null=True, blank=True, verbose_name="boolean answer")
    answer_number = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, verbose_name="numeric answer")
    answer_choices = models.JSONField(null=True, blank=True, verbose_name="selected choices")

    class Meta:
        verbose_name = "Application Answer"
        verbose_name_plural = "Application Answers"
        unique_together = [("application", "question")]

    def __str__(self):
        return f"Answer: {self.application_id} – {self.question_id}"


# Track stage changes over time (useful for analytics & auditing)
class ApplicationStatusHistory(TimeStampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="status_history", verbose_name="application")
    from_stage = models.CharField(max_length=15, choices=ApplicationStage.choices, verbose_name="from stage")
    to_stage = models.CharField(max_length=15, choices=ApplicationStage.choices, verbose_name="to stage")
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="application_stage_changes", verbose_name="changed by")
    note = models.TextField(blank=True, verbose_name="note")

    class Meta:
        verbose_name = "Application Stage Change"
        verbose_name_plural = "Application Stage Changes"
        ordering = ["-created_at"]


# ----------------------------
# Interviews & Feedback
# ----------------------------
class Interview(TimeStampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="interviews", verbose_name="application")
    interview_type = models.CharField(max_length=10, choices=InterviewType.choices, default=InterviewType.VIRTUAL, verbose_name="type")
    scheduled_at = models.DateTimeField(verbose_name="scheduled at")
    duration_minutes = models.PositiveIntegerField(default=60, validators=[MinValueValidator(5), MaxValueValidator(480)], verbose_name="duration (min)")
    location_text = models.CharField(max_length=200, blank=True, verbose_name="location (text)")
    meeting_url = models.URLField(blank=True, verbose_name="meeting URL")
    panel = models.ManyToManyField(User, blank=True, related_name="interviews_as_panel", verbose_name="interview panel")

    class Meta:
        verbose_name = "Interview"
        verbose_name_plural = "Interviews"
        ordering = ["scheduled_at"]

    def __str__(self):
        return f"Interview #{self.pk} – {self.application}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.scheduled_at < timezone.now():
            raise ValidationError("Interview cannot be scheduled in the past.")


class InterviewFeedback(TimeStampedModel):
    interview = models.ForeignKey(Interview, on_delete=models.CASCADE, related_name="feedback", verbose_name="interview")
    reviewer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="interview_feedback_given", verbose_name="reviewer")
    rating = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="rating (1-5)")
    recommendation = models.CharField(max_length=20, choices=[("STRONG_YES", "Strong Yes"), ("YES", "Yes"), ("NO", "No"), ("STRONG_NO", "Strong No")], verbose_name="recommendation")
    comments = models.TextField(blank=True, verbose_name="comments")

    class Meta:
        verbose_name = "Interview Feedback"
        verbose_name_plural = "Interview Feedback"

    def __str__(self):
        return f"Feedback by {self.reviewer_id} – Interview {self.interview_id}"


# ----------------------------
# Offers & Onboarding
# ----------------------------
class Offer(TimeStampedModel):
    application = models.OneToOneField(Application, on_delete=models.CASCADE, related_name="offer", verbose_name="application")
    status = models.CharField(max_length=10, choices=OfferStatus.choices, default=OfferStatus.DRAFT, verbose_name="status")
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="base salary")
    currency = models.CharField(max_length=10, default="NPR", verbose_name="currency")
    bonus = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="bonus")
    equity = models.CharField(max_length=50, blank=True, verbose_name="equity/benefits")
    start_date = models.DateField(blank=True, null=True, verbose_name="start date")
    sent_at = models.DateTimeField(blank=True, null=True, verbose_name="sent at")
    accepted_at = models.DateTimeField(blank=True, null=True, verbose_name="accepted at")
    offer_pdf = models.FileField(upload_to=upload_offer, blank=True, null=True, verbose_name="offer PDF")

    class Meta:
        verbose_name = "Offer"
        verbose_name_plural = "Offers"

    def __str__(self):
        return f"Offer – {self.application}"


class OnboardingTask(TimeStampedModel):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name="onboarding_tasks", verbose_name="application")
    title = models.CharField(max_length=150, verbose_name="title")
    description = models.TextField(blank=True, verbose_name="description")
    due_days_after_accept = models.IntegerField(default=7, verbose_name="due days after offer accept")
    is_completed = models.BooleanField(default=False, verbose_name="completed")
    assigned_to_department = models.ForeignKey(Department, null=True, blank=True, on_delete=models.SET_NULL, related_name="onboarding_tasks", verbose_name="assigned department")

    class Meta:
        verbose_name = "Onboarding Task"
        verbose_name_plural = "Onboarding Tasks"

    def __str__(self):
        return f"{self.title} – App {self.application_id}"

    @property
    def due_date(self):
        offer = getattr(self.application, "offer", None)
        if offer and offer.accepted_at:
            return (offer.accepted_at + timezone.timedelta(days=max(self.due_days_after_accept, 0))).date()
        return None


# ----------------------------
# Attachments / Notes / Activity
# ----------------------------
class Attachment(TimeStampedModel):
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="content type")
    object_id = models.PositiveIntegerField(verbose_name="object id")
    content_object = GenericForeignKey("content_type", "object_id")
    file = models.FileField(upload_to=upload_attachment, verbose_name="file")
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="job_attachments", verbose_name="uploaded by")
    caption = models.CharField(max_length=200, blank=True, verbose_name="caption")

    class Meta:
        verbose_name = "Attachment"
        verbose_name_plural = "Attachments"

    def __str__(self):
        return f"Attachment #{self.pk}"


class ActivityLog(TimeStampedModel):
    """Lightweight audit trail across Job/Candidate/Application etc."""
    actor = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="job_activity", verbose_name="actor")
    verb = models.CharField(max_length=60, verbose_name="action")
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, verbose_name="content type")
    object_id = models.PositiveIntegerField(verbose_name="object id")
    content_object = GenericForeignKey("content_type", "object_id")
    notes = models.TextField(blank=True, verbose_name="notes")

    class Meta:
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"
        indexes = [models.Index(fields=["content_type", "object_id", "created_at"])]

    def __str__(self):
        return f"{self.verb} by {self.actor_id} on {self.created_at:%Y-%m-%d}"
