# jobboard/views.py
from django.views.generic import ListView, DetailView
from django.db.models import Q, Prefetch
from django.utils import timezone

from .models import JobPosting, Department, Location, Specialty, EmploymentType, ShiftType, JobStatus

class CareersListView(ListView):
    template_name = "website/careers_list.html"
    model = JobPosting
    context_object_name = "jobs"
    paginate_by = 9

    def get_queryset(self):
        qs = JobPosting.objects.select_related("department", "location", "posted_by") \
            .prefetch_related("specialties", "credentials_required")

        # Default: show open and published
        status = self.request.GET.get("status", "OPEN")
        if status == "ALL":
            # show everything (admin-like browsing)
            pass
        elif status == "CLOSED":
            qs = qs.filter(status__in=[JobStatus.CLOSED, JobStatus.FILLED])
        else:
            # OPEN/PAUSED but also published and not past deadline
            today = timezone.localdate()
            qs = qs.filter(status__in=[JobStatus.OPEN, JobStatus.PAUSED]) \
                   .filter(Q(publish_at__isnull=True) | Q(publish_at__lte=timezone.now())) \
                   .filter(Q(application_deadline__isnull=True) | Q(application_deadline__gte=today))

        # Filters
        q = self.request.GET.get("q", "").strip()
        dept = self.request.GET.get("department")
        loc = self.request.GET.get("location")
        emp = self.request.GET.get("employment_type")
        shift = self.request.GET.get("shift")
        spec = self.request.GET.get("specialty")
        remote = self.request.GET.get("remote")
        exp_min = self.request.GET.get("exp_min")
        exp_max = self.request.GET.get("exp_max")
        posted = self.request.GET.get("posted")  # 7, 14, 30 (days)
        ordering = self.request.GET.get("order", "-created")

        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(description__icontains=q) |
                Q(short_description__icontains=q) |
                Q(tags__icontains=q) |
                Q(department__name__icontains=q) |
                Q(location__name__icontains=q) |
                Q(location__city__icontains=q) |
                Q(specialties__name__icontains=q)
            ).distinct()

        if dept:
            qs = qs.filter(department__slug=dept)
        if loc:
            qs = qs.filter(location__slug=loc)
        if emp:
            qs = qs.filter(employment_type=emp)
        if shift:
            qs = qs.filter(shift=shift)
        if spec:
            qs = qs.filter(specialties__slug=spec)

        if remote == "1":
            qs = qs.filter(remote_allowed=True)

        # Experience band (inclusive)
        try:
            if exp_min not in [None, ""]:
                qs = qs.filter(experience_min_years__gte=int(exp_min))
        except ValueError:
            pass
        try:
            if exp_max not in [None, ""]:
                # a job with exp_max=0 means "no upper limit" -> include it too
                qs = qs.filter(Q(experience_max_years=0) | Q(experience_max_years__lte=int(exp_max)))
        except ValueError:
            pass

        # Posted within last N days
        if posted and posted.isdigit():
            days = int(posted)
            since = timezone.now() - timezone.timedelta(days=days)
            qs = qs.filter(Q(publish_at__gte=since) | Q(created_at__gte=since))

        # Ordering
        if ordering == "created":
            qs = qs.order_by("created_at")
        elif ordering == "-created":
            qs = qs.order_by("-created_at")
        elif ordering == "deadline":
            qs = qs.order_by("application_deadline")
        elif ordering == "-deadline":
            qs = qs.order_by("-application_deadline")
        elif ordering == "title":
            qs = qs.order_by("title")
        elif ordering == "-title":
            qs = qs.order_by("-title")
        else:
            qs = qs.order_by("-created_at")

        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        # Filter choices
        ctx["departments"] = Department.objects.filter(active=True).order_by("priority", "name")
        ctx["locations"] = Location.objects.filter(active=True).order_by("country", "city", "name")
        ctx["specialties"] = Specialty.objects.all().order_by("name")
        ctx["employment_types"] = EmploymentType.choices
        ctx["shift_types"] = ShiftType.choices
        ctx["selected"] = {k: self.request.GET.get(k) for k in self.request.GET.keys()}

        # Build querystring sans 'page' to keep filters in pagination
        qd = self.request.GET.copy()
        qd.pop("page", None)
        ctx["querystring"] = qd.urlencode()

        # Page title/SEO helpers (optional)
        ctx["page_title"] = "Careers"
        return ctx


class CareerDetailView(DetailView):
    template_name = "website/career_detail.html"
    model = JobPosting
    context_object_name = "job"
    slug_field = "slug"
    slug_url_kwarg = "slug"

    def get_queryset(self):
        qs = JobPosting.objects.select_related("department", "location", "posted_by") \
            .prefetch_related("specialties", "credentials_required")
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        job = ctx["job"]
        ctx["can_apply"] = job.is_open
        ctx["apply_mailto"] = f"mailto:{job.apply_email}?subject=Application: {job.title} ({job.reference})" if job.apply_email else None
        ctx["page_title"] = f"Career – {job.title}"
        return ctx
