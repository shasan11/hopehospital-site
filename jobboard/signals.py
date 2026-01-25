# jobs/signals.py
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType

from .models import (
    JobPosting, JobStatus, Application, ApplicationStage, ApplicationStatusHistory,
    Offer, OfferStatus, ActivityLog
)

def _log(actor, verb, instance, notes=""):
    ActivityLog.objects.create(
        actor=actor,
        verb=verb,
        content_type=ContentType.objects.get_for_model(instance.__class__),
        object_id=instance.pk,
        notes=notes or "",
    )

@receiver(pre_save, sender=Application)
def sync_application_status(sender, instance: Application, **kwargs):
    if instance.pk:
        old = Application.objects.filter(pk=instance.pk).values("stage").first()
        if old and old["stage"] != instance.stage:
            # record history
            ApplicationStatusHistory.objects.create(
                application=instance,
                from_stage=old["stage"],
                to_stage=instance.stage,
                changed_by=None,  # set in view if you have request.user
            )
    # keep status mirrored
    instance.status = instance.stage

@receiver(post_save, sender=Application)
def log_application_changes(sender, instance: Application, created, **kwargs):
    if created:
        _log(actor=instance.candidate.user if instance.candidate and instance.candidate.user_id else None,
             verb="application_created", instance=instance,
             notes=f"Applied to {instance.job.reference}")
    else:
        _log(actor=None, verb="application_updated", instance=instance)

    # if rejected/withdrawn => nothing to do
    # if moved to HIRED, check job fill
    if instance.stage == ApplicationStage.HIRED:
        job = instance.job
        job.mark_filled_if_enough_hires()

@receiver(pre_save, sender=Offer)
def set_offer_timestamps(sender, instance: Offer, **kwargs):
    if instance.pk:
        old = Offer.objects.filter(pk=instance.pk).values("status").first()
        old_status = old["status"] if old else None
    else:
        old_status = None

    if instance.status == OfferStatus.SENT and not instance.sent_at:
        instance.sent_at = timezone.now()
    if instance.status == OfferStatus.ACCEPTED and not instance.accepted_at:
        instance.accepted_at = timezone.now()

    # Auto-advance application on acceptance
    if old_status != OfferStatus.ACCEPTED and instance.status == OfferStatus.ACCEPTED:
        app = instance.application
        if app.stage != ApplicationStage.HIRED:
            app.stage = ApplicationStage.HIRED
            app.status = ApplicationStage.HIRED
            app.save()

@receiver(post_save, sender=Offer)
def log_offer(sender, instance: Offer, created, **kwargs):
    _log(actor=None, verb="offer_created" if created else "offer_updated", instance=instance)

@receiver(pre_delete, sender=Application)
def prevent_delete_hired(sender, instance: Application, **kwargs):
    from django.core.exceptions import ValidationError
    if instance.stage == ApplicationStage.HIRED:
        raise ValidationError("Cannot delete an application that is HIRED.")

@receiver(pre_delete, sender=Offer)
def prevent_delete_accepted_offer(sender, instance: Offer, **kwargs):
    from django.core.exceptions import ValidationError
    if instance.status == OfferStatus.ACCEPTED:
        raise ValidationError("Cannot delete an accepted offer.")

@receiver(post_save, sender=JobPosting)
def auto_close_job_if_deadline_passed(sender, instance: JobPosting, **kwargs):
    instance.close_if_past_deadline()
