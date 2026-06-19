from datetime import timedelta

from django.db.models import Count, Max, Q
from django.utils import timezone

from accounts.models import CustomUser
from auditlogs.models import AuditLog
from core.models import Company

from .constants import SUBSCRIPTION_STATUS_PAST_DUE, SUBSCRIPTION_STATUS_TRIAL
from .models import (
    BillingInvoice,
    CompanyModule,
    CustomerSuccessEvent,
    CustomerSuccessProfile,
    RENEWAL_RISK_HIGH,
    RENEWAL_RISK_LOW,
    RENEWAL_RISK_MEDIUM,
    TenantSupportTicket,
)
from .module_service import ModuleLicensingService
from .usage_service import UsageLimitService


class CustomerSuccessService:

    @classmethod
    def _profile(cls, company):
        profile, _ = CustomerSuccessProfile.objects.get_or_create(company=company)
        return profile

    @classmethod
    def _login_activity(cls, company):
        users = CustomUser.objects.filter(company=company, is_active=True)
        total = users.count()
        since = timezone.now() - timedelta(days=30)
        active = users.filter(last_login__gte=since).count()
        last_login = users.aggregate(m=Max('last_login'))['m']
        return {
            'total_users': total,
            'active_users_30d': active,
            'login_rate': round(active / total * 100, 1) if total else 0,
            'last_login': last_login,
        }

    @classmethod
    def _feature_adoption(cls, company):
        modules = ModuleLicensingService.active_modules(company)
        usage = UsageLimitService.get_limits_snapshot(company)
        adopted = len(modules)
        plan_modules = CompanyModule.objects.filter(
            company=company, is_enabled=True,
        ).count()
        return {
            'modules_enabled': plan_modules,
            'modules_active': adopted,
            'usage': usage,
            'adoption_pct': min(100, adopted * 12) if adopted else 0,
        }

    @classmethod
    def _ticket_volume(cls, company):
        qs = TenantSupportTicket.objects.filter(company=company)
        open_count = qs.exclude(status__in=('resolved', 'closed')).count()
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_count = qs.filter(created_at__gte=month_start).count()
        return {'open': open_count, 'month': month_count}

    @classmethod
    def _compute_health_score(cls, login, adoption, tickets):
        login_score = min(100, float(login['login_rate']))
        adoption_score = min(100, float(adoption['adoption_pct']))
        ticket_score = max(0, 100 - tickets['open'] * 15 - tickets['month'] * 2)
        return max(0, min(100, int(
            login_score * 0.35 + adoption_score * 0.35 + ticket_score * 0.30,
        )))

    @classmethod
    def _compute_renewal_risk(cls, company, health_score, tickets, sub):
        if not sub or not sub.is_usable():
            return RENEWAL_RISK_HIGH
        if sub.status == SUBSCRIPTION_STATUS_PAST_DUE:
            return RENEWAL_RISK_HIGH
        if sub.status == SUBSCRIPTION_STATUS_TRIAL and sub.trial_ends_at:
            if sub.trial_ends_at <= timezone.now() + timedelta(days=14):
                return RENEWAL_RISK_HIGH
            if sub.trial_ends_at <= timezone.now() + timedelta(days=30):
                return RENEWAL_RISK_MEDIUM
        if health_score < 40 or tickets['open'] >= 3:
            return RENEWAL_RISK_HIGH
        if health_score < 65 or tickets['open'] >= 1:
            return RENEWAL_RISK_MEDIUM
        return RENEWAL_RISK_LOW

    @classmethod
    def company_snapshot(cls, company):
        sub = UsageLimitService.get_subscription(company)
        login = cls._login_activity(company)
        adoption = cls._feature_adoption(company)
        tickets = cls._ticket_volume(company)
        health_score = cls._compute_health_score(login, adoption, tickets)
        renewal_risk = cls._compute_renewal_risk(company, health_score, tickets, sub)
        profile = cls._profile(company)
        profile.health_score = health_score
        profile.renewal_risk = renewal_risk
        profile.feature_adoption = adoption
        profile.save(update_fields=[
            'health_score', 'renewal_risk', 'feature_adoption', 'updated_at',
        ])
        manager = None
        if profile.success_manager_id:
            manager = {
                'id': profile.success_manager_id,
                'name': profile.success_manager.get_full_name() or profile.success_manager.username,
                'email': profile.success_manager.email,
            }
        renewal_date = profile.renewal_date
        if not renewal_date and sub:
            if sub.trial_ends_at:
                renewal_date = sub.trial_ends_at.date()
            elif sub.current_period_end:
                renewal_date = sub.current_period_end.date()
        return {
            'company_id': company.id,
            'company_name': company.name,
            'health_score': health_score,
            'renewal_risk': renewal_risk,
            'renewal_date': renewal_date,
            'success_manager': manager,
            'login_activity': login,
            'feature_adoption': adoption,
            'ticket_volume': tickets,
            'subscription': {
                'plan': sub.plan.name if sub else None,
                'status': sub.status if sub else None,
                'trial_ends_at': sub.trial_ends_at if sub else None,
            },
        }

    @classmethod
    def renewal_alerts(cls):
        alerts = []
        for company in Company.objects.filter(is_active=True):
            snap = cls.company_snapshot(company)
            if snap['renewal_risk'] in (RENEWAL_RISK_HIGH, RENEWAL_RISK_MEDIUM):
                alerts.append({
                    'company_id': company.id,
                    'company_name': company.name,
                    'renewal_risk': snap['renewal_risk'],
                    'health_score': snap['health_score'],
                    'renewal_date': snap['renewal_date'],
                    'reason': cls._alert_reason(snap),
                })
        alerts.sort(key=lambda a: (0 if a['renewal_risk'] == RENEWAL_RISK_HIGH else 1, a['health_score']))
        return alerts

    @staticmethod
    def _alert_reason(snap):
        if snap['renewal_risk'] == RENEWAL_RISK_HIGH:
            if snap['ticket_volume']['open'] >= 3:
                return 'High open ticket volume'
            if snap['health_score'] < 40:
                return 'Low health score'
            return 'Renewal or subscription at risk'
        return 'Moderate renewal risk'

    @classmethod
    def dashboard(cls):
        companies = Company.objects.filter(is_active=True).order_by('name')
        rows = [cls.company_snapshot(c) for c in companies]
        alerts = cls.renewal_alerts()
        return {
            'companies': rows,
            'totals': {
                'companies': len(rows),
                'at_risk': sum(1 for r in rows if r['renewal_risk'] != RENEWAL_RISK_LOW),
                'avg_health': round(
                    sum(r['health_score'] for r in rows) / len(rows), 1,
                ) if rows else 0,
                'open_alerts': len(alerts),
            },
            'renewal_alerts': alerts[:20],
        }

    @classmethod
    def company_timeline(cls, company, limit=50):
        events = []
        for e in CustomerSuccessEvent.objects.filter(company=company)[:limit]:
            events.append({
                'type': e.event_type,
                'title': e.title,
                'body': e.body,
                'created_at': e.created_at,
                'source': 'cs_event',
            })
        for log in AuditLog.objects.filter(company=company).order_by('-created_at')[:limit]:
            events.append({
                'type': CustomerSuccessEvent.EVENT_AUDIT,
                'title': f'{log.module}: {log.action}',
                'body': log.description,
                'created_at': log.created_at,
                'source': 'audit',
            })
        for t in TenantSupportTicket.objects.filter(company=company).order_by('-created_at')[:limit]:
            events.append({
                'type': CustomerSuccessEvent.EVENT_TICKET,
                'title': t.subject,
                'body': t.status,
                'created_at': t.created_at,
                'source': 'support',
            })
        for inv in BillingInvoice.objects.filter(
            company=company, status='paid',
        ).order_by('-paid_at')[:limit]:
            events.append({
                'type': CustomerSuccessEvent.EVENT_BILLING,
                'title': inv.invoice_number,
                'body': f'Paid {inv.amount}',
                'created_at': inv.paid_at or inv.created_at,
                'source': 'billing',
            })
        events.sort(key=lambda e: e['created_at'] or timezone.now(), reverse=True)
        return events[:limit]

    @classmethod
    def company_detail(cls, company_id):
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            return None
        profile = cls._profile(company)
        snap = cls.company_snapshot(company)
        return {
            **snap,
            'meeting_notes': profile.meeting_notes,
            'timeline': cls.company_timeline(company),
        }

    @classmethod
    def update_company(cls, company_id, *, actor, data):
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            return None
        profile = cls._profile(company)
        if 'success_manager_id' in data:
            mgr = CustomUser.objects.filter(
                pk=data['success_manager_id'], is_superuser=True,
            ).first()
            profile.success_manager = mgr
        if 'renewal_date' in data:
            profile.renewal_date = data['renewal_date']
        if 'meeting_notes' in data:
            profile.meeting_notes = data['meeting_notes']
            CustomerSuccessEvent.objects.create(
                company=company,
                event_type=CustomerSuccessEvent.EVENT_MEETING,
                title='Meeting notes updated',
                body=data['meeting_notes'][:500],
                created_by=actor,
            )
        profile.save()
        return cls.company_detail(company_id)
