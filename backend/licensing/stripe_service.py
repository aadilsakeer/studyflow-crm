from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.utils import timezone

from .constants import (
    BILLING_CYCLE_MONTHLY,
    BILLING_CYCLE_YEARLY,
    SUBSCRIPTION_STATUS_ACTIVE,
    SUBSCRIPTION_STATUS_CANCELLED,
    SUBSCRIPTION_STATUS_PAST_DUE,
)
from .billing_notifications import notify_payment_failed, notify_payment_success
from .models import BillingPayment, CompanySubscription
from .subscription_service import SubscriptionService


class StripeBillingService:

    @staticmethod
    def _client():
        import stripe
        stripe.api_key = settings.STRIPE_SECRET_KEY
        return stripe

    @classmethod
    def is_configured(cls):
        return bool(getattr(settings, 'STRIPE_SECRET_KEY', ''))

    @classmethod
    def is_live_mode(cls):
        return getattr(settings, 'STRIPE_LIVE_MODE', False)

    @classmethod
    def create_checkout_session(cls, company, user, billing_cycle):
        if not cls.is_configured():
            raise ValueError('Stripe is not configured.')
        stripe = cls._client()
        subscription = CompanySubscription.objects.select_related('plan').get(company=company)
        plan = subscription.plan
        price_id = (
            plan.stripe_price_yearly_id if billing_cycle == BILLING_CYCLE_YEARLY
            else plan.stripe_price_monthly_id
        )
        if not price_id:
            raise ValueError('Stripe price not configured for this plan.')
        if not subscription.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email, name=company.name,
                metadata={'company_id': company.id},
            )
            subscription.stripe_customer_id = customer.id
            subscription.save(update_fields=['stripe_customer_id'])
        session = stripe.checkout.Session.create(
            mode='subscription',
            customer=subscription.stripe_customer_id,
            line_items=[{'price': price_id, 'quantity': 1}],
            success_url=settings.STRIPE_SUCCESS_URL,
            cancel_url=settings.STRIPE_CANCEL_URL,
            metadata={'company_id': company.id, 'billing_cycle': billing_cycle},
        )
        BillingPayment.objects.create(
            company=company, subscription=subscription,
            amount=plan.yearly_price if billing_cycle == BILLING_CYCLE_YEARLY else plan.monthly_price,
            currency='INR', status='pending', provider='stripe',
            provider_checkout_id=session.id,
            metadata={'billing_cycle': billing_cycle, 'live_mode': cls.is_live_mode()},
        )
        return session.url

    @classmethod
    def create_portal_session(cls, company):
        if not cls.is_configured():
            raise ValueError('Stripe is not configured.')
        subscription = CompanySubscription.objects.get(company=company)
        if not subscription.stripe_customer_id:
            raise ValueError('No Stripe customer on file.')
        session = cls._client().billing_portal.Session.create(
            customer=subscription.stripe_customer_id,
            return_url=settings.STRIPE_PORTAL_RETURN_URL,
        )
        return session.url

    @classmethod
    def cancel_at_period_end(cls, subscription):
        cls._client().Subscription.modify(
            subscription.stripe_subscription_id,
            cancel_at_period_end=True,
        )

    @classmethod
    def _sub_by_stripe_id(cls, stripe_sub_id):
        return CompanySubscription.objects.select_related(
            'company', 'plan',
        ).filter(stripe_subscription_id=stripe_sub_id).first()

    @classmethod
    def _handle_checkout_completed(cls, session):
        from core.models import Company
        company = Company.objects.get(pk=int(session['metadata']['company_id']))
        SubscriptionService.activate_paid(
            company,
            billing_cycle=session['metadata'].get('billing_cycle', BILLING_CYCLE_MONTHLY),
            provider_ids={
                'stripe_customer_id': session.get('customer', ''),
                'stripe_subscription_id': session.get('subscription', ''),
            },
        )

    @classmethod
    def _handle_invoice_paid(cls, invoice):
        sub = cls._sub_by_stripe_id(invoice.get('subscription'))
        if not sub or invoice.get('billing_reason') == 'subscription_create':
            return
        period_start = timezone.make_aware(
            datetime.fromtimestamp(invoice['period_start'], tz=dt_timezone.utc))
        period_end = timezone.make_aware(
            datetime.fromtimestamp(invoice['period_end'], tz=dt_timezone.utc))
        SubscriptionService.renew_period(
            sub.company, period_start=period_start, period_end=period_end,
            amount=invoice.get('amount_paid', 0) / 100,
            billing_cycle=sub.billing_cycle, provider='stripe',
            provider_invoice_id=invoice.get('id', ''),
        )

    @classmethod
    def _handle_invoice_failed(cls, invoice):
        sub = cls._sub_by_stripe_id(invoice.get('subscription'))
        if not sub:
            return
        SubscriptionService.update_status(sub.company, SUBSCRIPTION_STATUS_PAST_DUE)
        notify_payment_failed(sub.company, reason='Stripe invoice payment failed')

    @classmethod
    def _handle_subscription_updated(cls, stripe_sub):
        sub = cls._sub_by_stripe_id(stripe_sub['id'])
        if not sub:
            return
        status_map = {
            'active': SUBSCRIPTION_STATUS_ACTIVE,
            'past_due': SUBSCRIPTION_STATUS_PAST_DUE,
            'canceled': SUBSCRIPTION_STATUS_CANCELLED,
            'unpaid': SUBSCRIPTION_STATUS_PAST_DUE,
        }
        mapped = status_map.get(stripe_sub['status'])
        if mapped:
            SubscriptionService.update_status(
                sub.company, mapped,
                cancelled=mapped == SUBSCRIPTION_STATUS_CANCELLED,
            )

    @classmethod
    def handle_webhook(cls, payload, sig_header):
        if not cls.is_configured():
            return {'ignored': True}
        stripe = cls._client()
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        event_type, data = event['type'], event['data']['object']
        if event_type == 'checkout.session.completed':
            cls._handle_checkout_completed(data)
        elif event_type == 'invoice.paid':
            cls._handle_invoice_paid(data)
        elif event_type == 'invoice.payment_failed':
            cls._handle_invoice_failed(data)
        elif event_type == 'customer.subscription.updated':
            cls._handle_subscription_updated(data)
        return {'received': True}
