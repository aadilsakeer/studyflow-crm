import hashlib
import hmac
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
from .billing_notifications import notify_payment_failed
from .models import BillingPayment, CompanySubscription
from .subscription_service import SubscriptionService


class RazorpayBillingService:

    @classmethod
    def _client(cls):
        import razorpay
        return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

    @classmethod
    def is_configured(cls):
        return bool(getattr(settings, 'RAZORPAY_KEY_ID', '') and getattr(settings, 'RAZORPAY_KEY_SECRET', ''))

    @classmethod
    def verify_webhook_signature(cls, body, signature):
        secret = getattr(settings, 'RAZORPAY_WEBHOOK_SECRET', '')
        if not secret or not signature:
            return False
        expected = hmac.new(
            secret.encode(), body if isinstance(body, bytes) else body.encode(),
            hashlib.sha256,
        ).hexdigest()
        return hmac.compare_digest(expected, signature)

    @classmethod
    def create_subscription(cls, company, user, billing_cycle):
        if not cls.is_configured():
            raise ValueError('Razorpay is not configured.')
        client = cls._client()
        subscription = CompanySubscription.objects.select_related('plan').get(company=company)
        plan = subscription.plan
        plan_id = (
            plan.razorpay_plan_yearly_id if billing_cycle == BILLING_CYCLE_YEARLY
            else plan.razorpay_plan_monthly_id
        )
        if not plan_id:
            raise ValueError('Razorpay plan not configured.')
        payload = {
            'plan_id': plan_id,
            'total_count': 12 if billing_cycle == BILLING_CYCLE_YEARLY else 120,
            'customer_notify': 1,
            'notes': {'company_id': str(company.id), 'billing_cycle': billing_cycle},
        }
        if subscription.razorpay_customer_id:
            payload['customer_id'] = subscription.razorpay_customer_id
        else:
            customer = client.customer.create({
                'name': company.name, 'email': user.email,
                'contact': company.phone or '9999999999',
            })
            subscription.razorpay_customer_id = customer['id']
            subscription.save(update_fields=['razorpay_customer_id'])
            payload['customer_id'] = customer['id']
        rz_sub = client.subscription.create(payload)
        subscription.razorpay_subscription_id = rz_sub['id']
        subscription.save(update_fields=['razorpay_subscription_id'])
        amount = plan.yearly_price if billing_cycle == BILLING_CYCLE_YEARLY else plan.monthly_price
        BillingPayment.objects.create(
            company=company, subscription=subscription, amount=amount,
            currency='INR', status='pending', provider='razorpay',
            provider_checkout_id=rz_sub['id'],
            metadata={'billing_cycle': billing_cycle, 'short_url': rz_sub.get('short_url')},
        )
        return {'subscription_id': rz_sub['id'], 'short_url': rz_sub.get('short_url'), 'status': rz_sub.get('status')}

    @classmethod
    def _sub_for_entity(cls, entity):
        return CompanySubscription.objects.select_related('company', 'plan').filter(
            razorpay_subscription_id=entity.get('id', '')).first()

    @classmethod
    def _handle_activated(cls, entity):
        from core.models import Company
        company = Company.objects.get(pk=int(entity['notes']['company_id']))
        SubscriptionService.activate_paid(
            company,
            billing_cycle=entity['notes'].get('billing_cycle', BILLING_CYCLE_MONTHLY),
            provider_ids={'razorpay_subscription_id': entity['id']},
        )

    @classmethod
    def _handle_charged(cls, payload):
        entity = payload['payload']['subscription']['entity']
        sub = cls._sub_for_entity(entity)
        if not sub:
            cid = entity.get('notes', {}).get('company_id')
            if cid:
                sub = CompanySubscription.objects.select_related('company', 'plan').filter(
                    company_id=int(cid)).first()
        if not sub:
            return
        payment = payload['payload'].get('payment', {}).get('entity', {})
        amount = payment.get('amount', 0) / 100
        cs, ce = entity.get('current_start'), entity.get('current_end')
        period_start = datetime.fromtimestamp(cs, tz=dt_timezone.utc) if cs else timezone.now()
        period_end = datetime.fromtimestamp(ce, tz=dt_timezone.utc) if ce else timezone.now()
        if sub.status == SUBSCRIPTION_STATUS_ACTIVE and sub.current_period_end and sub.current_period_end >= period_end:
            return
        SubscriptionService.renew_period(
            sub.company, period_start=period_start, period_end=period_end,
            amount=amount or sub.plan.monthly_price, billing_cycle=sub.billing_cycle,
            provider='razorpay', provider_invoice_id=payment.get('id', ''),
        )

    @classmethod
    def _handle_failed(cls, payload):
        entity = payload['payload'].get('subscription', {}).get('entity', {})
        sub = cls._sub_for_entity(entity)
        if sub:
            SubscriptionService.update_status(sub.company, SUBSCRIPTION_STATUS_PAST_DUE)
            notify_payment_failed(sub.company, reason='Razorpay payment failed')

    @classmethod
    def _handle_cancelled(cls, entity):
        sub = cls._sub_for_entity(entity)
        if sub:
            SubscriptionService.update_status(sub.company, SUBSCRIPTION_STATUS_CANCELLED, cancelled=True)

    @classmethod
    def handle_webhook(cls, payload, raw_body=b'', signature=''):
        if not cls.is_configured():
            return {'ignored': True}
        if raw_body and signature and not cls.verify_webhook_signature(raw_body, signature):
            return {'error': 'invalid_signature'}, 400
        event = payload.get('event', '')
        if event == 'subscription.activated':
            cls._handle_activated(payload['payload']['subscription']['entity'])
        elif event == 'subscription.charged':
            cls._handle_charged(payload)
        elif event in ('subscription.pending', 'payment.failed'):
            cls._handle_failed(payload)
        elif event == 'subscription.cancelled':
            cls._handle_cancelled(payload['payload']['subscription']['entity'])
        return {'received': True}
