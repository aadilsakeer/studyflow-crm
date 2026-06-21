from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone

from accounts.models import CustomUser
from admissions.models import Student, StudentDocument
from leads.models import Lead
from whatsapp.models import WhatsAppMessage

from .constants import (
    LIMIT_LEADS,
    LIMIT_STORAGE,
    LIMIT_STUDENTS,
    LIMIT_USERS,
    LIMIT_WHATSAPP,
)
from .exceptions import LimitExceededError, SubscriptionInactiveError
from .models import CompanySubscription


class UsageLimitService:

    METRIC_FIELDS = {
        LIMIT_USERS: 'max_users',
        LIMIT_LEADS: 'max_leads',
        LIMIT_STUDENTS: 'max_students',
        LIMIT_WHATSAPP: 'max_whatsapp_per_month',
        LIMIT_STORAGE: 'max_storage_mb',
    }

    @staticmethod
    def get_subscription(company):
        if not company:
            return None

        return CompanySubscription.objects.filter(
            company=company,
        ).select_related('plan').first()

    @classmethod
    def require_active_subscription(cls, company):
        subscription = cls.get_subscription(company)

        if not subscription:
            from .subscription_service import SubscriptionService

            try:
                subscription = SubscriptionService.start_trial(company)
            except ValueError:
                raise SubscriptionInactiveError(
                    'Your subscription is inactive or trial has expired.',
                )

        if not subscription.is_usable():
            raise SubscriptionInactiveError(
                'Your subscription is inactive or trial has expired.',
            )

        return subscription

    @classmethod
    def get_usage(cls, company, metric):
        if metric == LIMIT_USERS:
            return CustomUser.objects.filter(
                company=company,
                is_active=True,
            ).count()

        if metric == LIMIT_LEADS:
            return Lead.objects.filter(
                company=company,
                is_deleted=False,
            ).count()

        if metric == LIMIT_STUDENTS:
            return Student.objects.filter(
                company=company,
                is_deleted=False,
            ).count()

        if metric == LIMIT_WHATSAPP:
            start = timezone.now().replace(
                day=1,
                hour=0,
                minute=0,
                second=0,
                microsecond=0,
            )
            return WhatsAppMessage.objects.filter(
                company=company,
                created_at__gte=start,
            ).count()

        if metric == LIMIT_STORAGE:
            total_bytes = StudentDocument.objects.filter(
                company=company,
                is_deleted=False,
            ).aggregate(total=Sum('file_size'))['total'] or 0
            return int(total_bytes / (1024 * 1024)) + 1

        return 0

    @classmethod
    def get_limits_snapshot(cls, company):
        subscription = cls.get_subscription(company)
        plan = subscription.plan if subscription else None
        metrics = (
            LIMIT_USERS,
            LIMIT_LEADS,
            LIMIT_STUDENTS,
            LIMIT_WHATSAPP,
            LIMIT_STORAGE,
        )
        snapshot = {}

        for metric in metrics:
            limit = None
            if plan:
                limit = getattr(
                    plan,
                    cls.METRIC_FIELDS[metric],
                    None,
                )
            snapshot[metric] = {
                'used': cls.get_usage(company, metric),
                'limit': limit,
            }

        return snapshot

    @classmethod
    def check(cls, company, metric, increment=1):
        subscription = cls.require_active_subscription(company)
        plan = subscription.plan
        field = cls.METRIC_FIELDS[metric]
        limit = getattr(plan, field, None)

        if limit is None:
            return True

        used = cls.get_usage(company, metric)

        if used + increment > limit:
            raise LimitExceededError(
                f'Plan limit reached for {metric.replace("_", " ")} '
                f'({used}/{limit}). Upgrade your subscription.',
            )

        return True

    @classmethod
    def add_storage_mb(cls, company, mb_delta):
        cls.check(company, LIMIT_STORAGE, increment=mb_delta)

        from .models import CompanySettings

        settings, _ = CompanySettings.objects.get_or_create(
            company=company,
        )
        settings.storage_used_mb = max(
            0,
            settings.storage_used_mb + mb_delta,
        )
        settings.save(update_fields=['storage_used_mb', 'updated_at'])
