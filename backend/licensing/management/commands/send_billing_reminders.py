from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

from core.models import Company
from licensing.billing_notifications import notify_renewal_reminder, notify_trial_expiring
from licensing.models import CompanySettings, CompanySubscription


class Command(BaseCommand):
    help = 'Send trial expiry and renewal reminder emails'

    def handle(self, *args, **options):
        now = timezone.now()
        sent = 0

        for sub in CompanySubscription.objects.filter(status='trial').select_related('company'):
            if not sub.trial_ends_at:
                continue
            days = (sub.trial_ends_at - now).days
            if days in (7, 3, 1):
                if notify_trial_expiring(sub.company, days):
                    sent += 1

        renew_window = now + timedelta(days=3)
        for sub in CompanySubscription.objects.filter(
            status='active',
            current_period_end__lte=renew_window,
            current_period_end__gte=now,
        ).select_related('company'):
            if notify_renewal_reminder(sub.company, sub.current_period_end.date()):
                sent += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {sent} billing reminders'))
