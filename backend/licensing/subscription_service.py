from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from accounts.models import CustomUser, Role
from accounts.constants import ROLE_ADMIN
from core.models import Company

from .constants import (
    BILLING_CYCLE_MONTHLY,
    SUBSCRIPTION_STATUS_ACTIVE,
    SUBSCRIPTION_STATUS_CANCELLED,
    SUBSCRIPTION_STATUS_EXPIRED,
    SUBSCRIPTION_STATUS_PAST_DUE,
    SUBSCRIPTION_STATUS_TRIAL,
)
from .models import (
    BillingInvoice,
    BillingPayment,
    CompanyModule,
    CompanySettings,
    CompanySubscription,
    PlanModule,
    SubscriptionPlan,
)


class SubscriptionService:

    @staticmethod
    def get_default_plan():
        return SubscriptionPlan.objects.filter(
            is_active=True,
        ).order_by('sort_order').first()

    @classmethod
    def sync_plan_modules(cls, company, plan):
        enabled_ids = PlanModule.objects.filter(
            plan=plan,
        ).values_list('module_id', flat=True)

        for module_id in enabled_ids:
            CompanyModule.objects.update_or_create(
                company=company,
                module_id=module_id,
                defaults={
                    'is_enabled': True,
                    'from_plan': True,
                    'is_trial': False,
                },
            )

    @classmethod
    @transaction.atomic
    def start_trial(cls, company, plan=None):
        plan = plan or cls.get_default_plan()

        if not plan:
            raise ValueError('No subscription plan configured.')

        now = timezone.now()
        trial_end = now + timedelta(days=plan.trial_days)

        subscription, _ = CompanySubscription.objects.update_or_create(
            company=company,
            defaults={
                'plan': plan,
                'status': SUBSCRIPTION_STATUS_TRIAL,
                'billing_cycle': BILLING_CYCLE_MONTHLY,
                'start_date': now.date(),
                'trial_ends_at': trial_end,
                'current_period_start': now,
                'current_period_end': trial_end,
                'is_active': True,
                'cancelled_at': None,
            },
        )

        cls.sync_plan_modules(company, plan)
        return subscription

    @classmethod
    @transaction.atomic
    def activate_paid(cls, company, *, billing_cycle, provider_ids=None):
        provider_ids = provider_ids or {}
        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )
        now = timezone.now()

        if billing_cycle == 'yearly':
            period_end = now + timedelta(days=365)
        else:
            period_end = now + timedelta(days=30)

        subscription.status = SUBSCRIPTION_STATUS_ACTIVE
        subscription.billing_cycle = billing_cycle
        subscription.trial_ends_at = None
        subscription.current_period_start = now
        subscription.current_period_end = period_end
        subscription.is_active = True
        subscription.cancelled_at = None

        for key, value in provider_ids.items():
            if value:
                setattr(subscription, key, value)

        subscription.save()
        cls.sync_plan_modules(company, subscription.plan)
        cls._record_paid_invoice(company, subscription, billing_cycle, now, period_end)
        return subscription

    @classmethod
    def _record_paid_invoice(cls, company, subscription, billing_cycle, now, period_end):
        from .constants import INVOICE_STATUS_PAID, PAYMENT_STATUS_PAID

        plan = subscription.plan
        amount = (
            plan.yearly_price
            if billing_cycle == 'yearly'
            else plan.monthly_price
        )

        invoice = BillingInvoice.objects.create(
            company=company,
            subscription=subscription,
            invoice_number=cls.generate_invoice_number(company.id),
            amount=amount,
            status=INVOICE_STATUS_PAID,
            period_start=now.date(),
            period_end=period_end.date(),
            paid_at=now,
            line_items=[{
                'description': f'{plan.name} ({billing_cycle})',
                'amount': str(amount),
            }],
        )

        BillingPayment.objects.filter(
            company=company,
            status='pending',
        ).update(
            status=PAYMENT_STATUS_PAID,
            paid_at=now,
            invoice=invoice,
        )
        from .billing_notifications import notify_payment_success
        notify_payment_success(company, amount, invoice.invoice_number)

    @staticmethod
    def generate_invoice_number(company_id):
        count = BillingInvoice.objects.filter(
            company_id=company_id,
        ).count()
        return f'GV-{company_id:04d}-{count + 1:05d}'

    @classmethod
    @transaction.atomic
    def change_plan(cls, company, plan_code):
        plan = SubscriptionPlan.objects.filter(
            code=plan_code,
            is_active=True,
        ).first()

        if not plan:
            raise ValueError('Plan not found.')

        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )

        if subscription.status != SUBSCRIPTION_STATUS_TRIAL:
            raise ValueError(
                'Plan changes during trial only. Use checkout to upgrade.',
            )

        subscription.plan = plan
        subscription.save(update_fields=['plan', 'updated_at'])
        cls.sync_plan_modules(company, plan)
        return subscription

    @classmethod
    @transaction.atomic
    def renew_period(cls, company, *, period_start, period_end, amount,
                     billing_cycle, provider='manual', provider_invoice_id=''):
        from .constants import INVOICE_STATUS_PAID, PAYMENT_STATUS_PAID

        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )
        subscription.status = SUBSCRIPTION_STATUS_ACTIVE
        subscription.current_period_start = period_start
        subscription.current_period_end = period_end
        subscription.is_active = True
        subscription.save()

        invoice = BillingInvoice.objects.create(
            company=company,
            subscription=subscription,
            invoice_number=cls.generate_invoice_number(company.id),
            amount=amount,
            status=INVOICE_STATUS_PAID,
            period_start=period_start.date() if hasattr(period_start, 'date') else period_start,
            period_end=period_end.date() if hasattr(period_end, 'date') else period_end,
            paid_at=timezone.now(),
            stripe_invoice_id=provider_invoice_id if provider == 'stripe' else '',
            razorpay_invoice_id=provider_invoice_id if provider == 'razorpay' else '',
            line_items=[{
                'description': f'{subscription.plan.name} renewal ({billing_cycle})',
                'amount': str(amount),
            }],
        )

        BillingPayment.objects.create(
            company=company,
            subscription=subscription,
            invoice=invoice,
            amount=amount,
            status=PAYMENT_STATUS_PAID,
            provider=provider,
            provider_payment_id=provider_invoice_id,
            paid_at=timezone.now(),
        )
        from .billing_notifications import notify_payment_success

        notify_payment_success(company, amount, invoice.invoice_number)
        return subscription

    @classmethod
    @transaction.atomic
    def update_status(cls, company, status, *, cancelled=False):
        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )
        subscription.status = status

        if cancelled:
            subscription.cancelled_at = timezone.now()
            subscription.auto_renew = False
            if status == SUBSCRIPTION_STATUS_CANCELLED:
                subscription.is_active = False

        subscription.save()
        return subscription

    @classmethod
    @transaction.atomic
    def cancel_subscription(cls, company):
        from .constants import SUBSCRIPTION_STATUS_CANCELLED
        from .stripe_service import StripeBillingService

        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )
        if subscription.stripe_subscription_id and StripeBillingService.is_configured():
            StripeBillingService.cancel_at_period_end(subscription)

        subscription.status = SUBSCRIPTION_STATUS_CANCELLED
        subscription.cancelled_at = timezone.now()
        subscription.auto_renew = False
        subscription.is_active = False
        subscription.save()
        return subscription

    @classmethod
    @transaction.atomic
    def downgrade_plan(cls, company, plan_code):
        plan = SubscriptionPlan.objects.filter(code=plan_code, is_active=True).first()
        if not plan:
            raise ValueError('Plan not found.')

        subscription = CompanySubscription.objects.select_for_update().get(
            company=company,
        )
        current = subscription.plan
        if plan.sort_order >= current.sort_order and subscription.status != SUBSCRIPTION_STATUS_TRIAL:
            raise ValueError('Select a lower-tier plan to downgrade.')

        subscription.plan = plan
        subscription.save(update_fields=['plan', 'updated_at'])
        cls.sync_plan_modules(company, plan)
        return subscription


class OnboardingService:

    @classmethod
    @transaction.atomic
    def register_tenant(cls, *, company_name, admin_email, admin_password,
                        admin_first_name='', admin_last_name='', plan_code=None):
        plan = None
        if plan_code:
            plan = SubscriptionPlan.objects.filter(
                code=plan_code,
                is_active=True,
            ).first()

        company = Company.objects.create(
            name=company_name,
            email=admin_email,
        )
        CompanySettings.objects.create(
            company=company,
            billing_email=admin_email,
            brand_name=company_name,
        )
        SubscriptionService.start_trial(company, plan=plan)

        admin_role = Role.objects.filter(name=ROLE_ADMIN).first()
        user = CustomUser.objects.create_user(
            username=admin_email,
            email=admin_email,
            password=admin_password,
            first_name=admin_first_name,
            last_name=admin_last_name,
            company=company,
            role=admin_role,
        )

        return company, user

    @classmethod
    def advance_onboarding(cls, company, step):
        settings = CompanySettings.objects.get(company=company)
        settings.onboarding_step = step

        if step >= 3 and not settings.onboarding_completed_at:
            settings.onboarding_completed_at = timezone.now()

        settings.save(
            update_fields=[
                'onboarding_step',
                'onboarding_completed_at',
                'updated_at',
            ],
        )
        return settings
