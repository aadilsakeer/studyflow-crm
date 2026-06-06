from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Lead, LeadTimeline


@receiver(post_save, sender=Lead)
def create_lead_timeline(sender, instance, created, **kwargs):

    if created:
        LeadTimeline.objects.create(
            lead=instance,
            action="Lead Created",
            description=f"Lead {instance.first_name} {instance.last_name} was created."
        )