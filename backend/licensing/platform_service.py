from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from core.models import Company

from .constants import SUBSCRIPTION_STATUS_TRIAL
from .models import CompanySettings, CompanySubscription, SubscriptionPlan
from .subscription_service import SubscriptionService


class PlatformOpsService:

    @staticmethod
    @transaction.atomic
    def set_company_active(company_id, is_active):
        company = Company.objects.select_for_update().get(pk=company_id)
        company.is_active = is_active
        company.save(update_fields=['is_active'])
        return company

    @staticmethod
    @transaction.atomic
    def admin_change_plan(company_id, plan_code):
        plan = SubscriptionPlan.objects.filter(code=plan_code, is_active=True).first()
        if not plan:
            raise ValueError('Plan not found.')
        company = Company.objects.get(pk=company_id)
        sub = CompanySubscription.objects.select_for_update().get(company=company)
        sub.plan = plan
        sub.save(update_fields=['plan', 'updated_at'])
        SubscriptionService.sync_plan_modules(company, plan)
        return sub

    @staticmethod
    @transaction.atomic
    def extend_trial(company_id, days=7):
        sub = CompanySubscription.objects.select_for_update().get(
            company_id=company_id,
        )
        base = sub.trial_ends_at or timezone.now()
        sub.trial_ends_at = base + timedelta(days=days)
        sub.status = SUBSCRIPTION_STATUS_TRIAL
        sub.is_active = True
        sub.save()
        return sub

    @staticmethod
    def reset_usage(company_id):
        CompanySettings.objects.filter(company_id=company_id).update(
            storage_used_mb=0,
        )
        return True
