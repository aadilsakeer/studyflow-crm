from decimal import Decimal

from django.db import transaction
from django.db.models import Count, Sum
from django.utils import timezone

from accounts.constants import ROLE_ADMIN
from accounts.models import CustomUser
from accounts.password_service import UserPasswordService, generate_temp_password
from admissions.models import Student, StudentDocument
from auditlogs.models import AuditLog
from auditlogs.serializers import AuditLogSerializer
from core.models import Company
from leads.models import Lead
from whatsapp.models import WhatsAppMessage

from core.operations import operations_snapshot

from .constants import SUBSCRIPTION_STATUS_CANCELLED
from .models import BillingInvoice, BillingPayment, CompanySubscription, TenantSupportTicket
from .subscription_service import OnboardingService, SubscriptionService
from .module_service import ModuleLicensingService
from .usage_service import UsageLimitService


class OwnerConsoleService:

    @staticmethod
    def dashboard():
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        revenue = BillingInvoice.objects.filter(status='paid').aggregate(
            t=Sum('amount'),
        )['t'] or Decimal('0')

        monthly_revenue = BillingInvoice.objects.filter(
            status='paid', paid_at__gte=month_start,
        ).aggregate(t=Sum('amount'))['t'] or Decimal('0')

        mrr = Decimal('0')
        for sub in CompanySubscription.objects.filter(
            status__in=('active', 'trial'),
        ).select_related('plan'):
            plan = sub.plan
            if sub.billing_cycle == 'yearly':
                mrr += plan.yearly_price / 12
            else:
                mrr += plan.monthly_price

        return {
            'totals': {
                'companies': Company.objects.count(),
                'users': CustomUser.objects.filter(is_active=True).count(),
                'leads': Lead.objects.filter(is_deleted=False).count(),
                'students': Student.objects.filter(is_deleted=False).count(),
                'mrr': mrr,
                'arr': mrr * 12,
                'revenue': revenue,
                'monthly_revenue': monthly_revenue,
                'open_tickets': TenantSupportTicket.objects.exclude(
                    status__in=('resolved', 'closed'),
                ).count(),
            },
            'health': operations_snapshot(),
        }

    @staticmethod
    def list_companies():
        rows = []
        for company in Company.objects.order_by('-created_at')[:200]:
            sub = UsageLimitService.get_subscription(company)
            rows.append({
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'is_active': company.is_active,
                'users': CustomUser.objects.filter(company=company, is_active=True).count(),
                'plan': sub.plan.name if sub else None,
                'status': sub.status if sub else None,
                'created_at': company.created_at,
            })
        return rows

    @staticmethod
    def company_deep_view(company_id):
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            return None

        sub = UsageLimitService.get_subscription(company)
        usage = UsageLimitService.get_limits_snapshot(company)
        month_start = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)

        admin_user = CustomUser.objects.filter(
            company=company,
            role__name=ROLE_ADMIN,
            is_active=True,
        ).first()

        return {
            'company': {
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'phone': company.phone,
                'is_active': company.is_active,
                'created_at': company.created_at,
            },
            'subscription': {
                'plan': sub.plan.name if sub else None,
                'status': sub.status if sub else None,
                'trial_ends_at': sub.trial_ends_at if sub else None,
                'billing_cycle': sub.billing_cycle if sub else None,
            },
            'usage': usage,
            'counts': {
                'users': CustomUser.objects.filter(company=company, is_active=True).count(),
                'leads': Lead.objects.filter(company=company, is_deleted=False).count(),
                'students': Student.objects.filter(company=company, is_deleted=False).count(),
                'documents': StudentDocument.objects.filter(company=company, is_deleted=False).count(),
                'whatsapp_month': WhatsAppMessage.objects.filter(
                    company=company, created_at__gte=month_start,
                ).count(),
            },
            'admin_user_id': admin_user.id if admin_user else None,
            'billing': list(BillingInvoice.objects.filter(company=company).order_by(
                '-created_at',
            )[:20].values('invoice_number', 'amount', 'status', 'paid_at', 'created_at')),
            'payments': list(BillingPayment.objects.filter(company=company).order_by(
                '-created_at',
            )[:20].values('amount', 'status', 'provider', 'created_at')),
            'support': list(TenantSupportTicket.objects.filter(company=company).order_by(
                '-created_at',
            )[:20].values('id', 'subject', 'status', 'priority', 'created_at')),
            'audit_logs': AuditLogSerializer(
                AuditLog.objects.filter(company=company).order_by('-created_at')[:30],
                many=True,
            ).data,
            'modules': ModuleLicensingService.company_modules(company),
        }

    @staticmethod
    def create_company(*, name, email, admin_email, admin_password):
        return OnboardingService.register_tenant(
            company_name=name,
            admin_email=admin_email or email,
            admin_password=admin_password,
            plan_code=None,
        )

    @classmethod
    @transaction.atomic
    def onboard_tenant(
        cls,
        *,
        name,
        email,
        admin_email,
        plan_code=None,
        module_codes=None,
        admin_first_name='',
        admin_last_name='',
        actor=None,
    ):
        temp_password = generate_temp_password()
        company, user = OnboardingService.register_tenant(
            company_name=name,
            admin_email=admin_email or email,
            admin_password=temp_password,
            admin_first_name=admin_first_name,
            admin_last_name=admin_last_name,
            plan_code=plan_code,
        )
        if email:
            company.email = email
            company.save(update_fields=['email'])

        if plan_code:
            from .platform_service import PlatformOpsService
            PlatformOpsService.admin_change_plan(company.id, plan_code)

        for code in module_codes or []:
            try:
                ModuleLicensingService.enable_module(company, code, actor=actor)
            except ValueError:
                pass

        return {
            'company_id': company.id,
            'company_name': company.name,
            'admin_id': user.id,
            'admin_username': user.username,
            'admin_email': user.email,
            'temporary_password': temp_password,
            'plan_code': plan_code,
            'module_codes': module_codes or [],
        }

    @staticmethod
    def reset_user_password(user_id, *, actor):
        user = CustomUser.objects.filter(pk=user_id).first()
        if not user:
            return None
        temp = UserPasswordService.reset_password(user, actor=actor)
        return {'user_id': user.id, 'username': user.username, 'temporary_password': temp}

    @staticmethod
    def set_user_active(user_id, *, active, actor):
        user = CustomUser.objects.filter(pk=user_id).first()
        if not user:
            return None
        if active:
            UserPasswordService.unlock_user(user, actor=actor)
        else:
            UserPasswordService.disable_user(user, actor=actor)
        return {'user_id': user.id, 'username': user.username, 'is_active': user.is_active}

    @staticmethod
    def delete_company(company_id):
        company = Company.objects.get(pk=company_id)
        company.is_active = False
        company.save(update_fields=['is_active'])
        sub = CompanySubscription.objects.filter(company=company).first()
        if sub:
            sub.status = SUBSCRIPTION_STATUS_CANCELLED
            sub.is_active = False
            sub.save(update_fields=['status', 'is_active'])
        return company
