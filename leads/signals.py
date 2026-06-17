from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver

from .models import Lead, LeadTimeline, FollowUp, CallLog


@receiver(post_save, sender=Lead)
def create_lead_timeline(sender, instance, created, **kwargs):

    if created:

        instance.score = 5

        LeadTimeline.objects.create(
            lead=instance,
            action="Lead Created",
            description=(
                f"Lead {instance.first_name} "
                f"{instance.last_name} was created."
            ),
        )

        instance.save()


@receiver(pre_save, sender=Lead)
def store_lead_status(sender, instance, **kwargs):

    if not instance.pk:
        return

    try:
        old = Lead.objects.get(pk=instance.pk)
        instance._old_status = old.status
    except Lead.DoesNotExist:
        instance._old_status = None


@receiver(post_save, sender=Lead)
def log_lead_status_change(
    sender,
    instance,
    created,
    **kwargs,
):

    if created:
        return

    old_status = getattr(
        instance,
        "_old_status",
        None,
    )

    if (
        old_status
        and old_status != instance.status
    ):
        LeadTimeline.objects.create(
            lead=instance,
            action="Status Changed",
            description=(
                f"Status changed from "
                f"{old_status} to "
                f"{instance.status}."
            ),
        )


@receiver(post_save, sender=Lead)
def update_lead_score(sender, instance, **kwargs):

    score_map = {
        "new": 5,
        "contacted": 10,
        "follow_up": 20,
        "interested": 30,
        "converted": 100,
        "lost": 0,
        "not_interested": 0,
    }

    new_score = score_map.get(
        instance.status,
        0,
    )

    if instance.score != new_score:
        Lead.objects.filter(
            pk=instance.pk,
        ).update(
            score=new_score,
        )


@receiver(pre_save, sender=FollowUp)
def store_follow_up_completed(sender, instance, **kwargs):
    if not instance.pk:
        instance._was_completed = False
        return

    try:
        old = FollowUp.objects.get(pk=instance.pk)
        instance._was_completed = old.completed
    except FollowUp.DoesNotExist:
        instance._was_completed = False


@receiver(post_save, sender=FollowUp)
def log_follow_up_timeline(
    sender,
    instance,
    created,
    **kwargs,
):

    if created:
        LeadTimeline.objects.create(
            lead=instance.lead,
            action="Follow Up Added",
            description=(
                instance.notes
                or "Follow up scheduled."
            ),
            performed_by=instance.assigned_to,
        )
        return

    was_completed = getattr(
        instance,
        "_was_completed",
        False,
    )

    if (
        instance.completed
        and not was_completed
    ):
        LeadTimeline.objects.create(
            lead=instance.lead,
            action="Follow Up Completed",
            description=(
                instance.notes
                or "Follow up marked complete."
            ),
            performed_by=instance.assigned_to,
        )


@receiver(post_save, sender=CallLog)
def log_call_timeline(
    sender,
    instance,
    created,
    **kwargs,
):

    if not created:
        return

    description = instance.outcome

    if instance.notes:
        description = (
            f"{instance.outcome}. "
            f"{instance.notes}"
        )

    LeadTimeline.objects.create(
        lead=instance.lead,
        action="Call Logged",
        description=description,
        performed_by=instance.called_by,
    )
