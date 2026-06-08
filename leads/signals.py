from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead, LeadTimeline


@receiver(post_save, sender=Lead)
def create_lead_timeline(sender, instance, created, **kwargs):

    if created:

        instance.score = 5

        LeadTimeline.objects.create(
            lead=instance,
            action="Lead Created",
            description=f"Lead {instance.first_name} {instance.last_name} was created."
        )

        instance.save()


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

    new_score = score_map.get(instance.status, 0)

    if instance.score != new_score:
        Lead.objects.filter(pk=instance.pk).update(
            score=new_score
        )