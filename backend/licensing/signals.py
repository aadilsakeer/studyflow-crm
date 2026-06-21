from django.db.models.signals import pre_save
from django.dispatch import receiver

from accounts.models import CustomUser

from .constants import LIMIT_USERS
from .usage_service import UsageLimitService


@receiver(pre_save, sender=CustomUser)
def enforce_user_limit_on_create(sender, instance, **kwargs):
    if instance.pk or not instance.company_id or not instance.is_active:
        return

    UsageLimitService.check(instance.company, LIMIT_USERS)
