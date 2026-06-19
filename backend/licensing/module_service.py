from datetime import timedelta

from django.db import transaction
from django.utils import timezone

from auditlogs.services import AuditLogService
from core.models import Company

from .constants import (
    AUDIT_MODULE_LICENSING,
    LIMIT_LEADS,
    LIMIT_STORAGE,
    LIMIT_STUDENTS,
    LIMIT_WHATSAPP,
    MODULE_CATALOG,
)
from .models import CompanyModule, Module, PlanModule, SubscriptionPlan
from .usage_service import UsageLimitService


MODULE_USAGE_METRICS = {
    'whatsapp': LIMIT_WHATSAPP,
    'crm': LIMIT_LEADS,
    'admissions': LIMIT_STUDENTS,
    'document_intelligence': LIMIT_STORAGE,
    'studentportal': LIMIT_STUDENTS,
}


class ModuleLicensingService:

    @staticmethod
    def _audit(company, user, action, object_id, description):
        AuditLogService.log(
            company=company,
            user=user,
            module=AUDIT_MODULE_LICENSING,
            action=action,
            object_id=object_id,
            description=description,
        )

    @staticmethod
    def _get_module(code):
        mod = Module.objects.filter(code=code, is_active=True).first()
        if not mod:
            raise ValueError(f'Unknown module: {code}')
        return mod

    @classmethod
    def catalog(cls):
        modules = {
            m.code: {
                'id': m.id,
                'name': m.name,
                'code': m.code,
                'description': m.description,
                'is_active': m.is_active,
            }
            for m in Module.objects.filter(is_active=True).order_by('name')
        }
        plans = []
        for plan in SubscriptionPlan.objects.filter(is_active=True).order_by('sort_order'):
            plan_modules = list(
                PlanModule.objects.filter(plan=plan)
                .select_related('module')
                .values_list('module__code', flat=True),
            )
            plans.append({
                'id': plan.id,
                'name': plan.name,
                'code': plan.code,
                'modules': plan_modules,
            })
        return {'modules': modules, 'plans': plans, 'catalog': MODULE_CATALOG}

    @classmethod
    def company_modules(cls, company):
        rows = []
        for cm in CompanyModule.objects.filter(
            company=company,
        ).select_related('module').order_by('module__name'):
            rows.append(cls._serialize_company_module(company, cm))
        return rows

    @classmethod
    def _serialize_company_module(cls, company, cm):
        usage = cls.module_usage(company, cm.module.code)
        return {
            'module_id': cm.module_id,
            'code': cm.module.code,
            'name': cm.module.name,
            'is_enabled': cm.is_enabled,
            'is_trial': cm.is_trial,
            'expires_at': cm.expires_at,
            'usage_limits': cm.usage_limits or {},
            'from_plan': cm.from_plan,
            'is_accessible': cm.is_accessible(),
            'usage': usage,
        }

    @classmethod
    def module_usage(cls, company, module_code):
        metric = MODULE_USAGE_METRICS.get(module_code)
        if not metric:
            return {'used': None, 'limit': None}
        snapshot = UsageLimitService.get_limits_snapshot(company)
        return snapshot.get(metric, {'used': None, 'limit': None})

    @classmethod
    @transaction.atomic
    def enable_module(cls, company, module_code, *, actor=None, expires_at=None, usage_limits=None):
        mod = cls._get_module(module_code)
        cm, created = CompanyModule.objects.update_or_create(
            company=company,
            module=mod,
            defaults={
                'is_enabled': True,
                'is_trial': False,
                'expires_at': expires_at,
                'usage_limits': usage_limits or {},
                'from_plan': False,
            },
        )
        cls._audit(
            company, actor, 'enable_module', cm.id,
            f'Enabled module {mod.code}',
        )
        return cls._serialize_company_module(company, cm)

    @classmethod
    @transaction.atomic
    def disable_module(cls, company, module_code, *, actor=None):
        mod = cls._get_module(module_code)
        cm = CompanyModule.objects.filter(company=company, module=mod).first()
        if not cm:
            raise ValueError(f'Module {module_code} not assigned.')
        cm.is_enabled = False
        cm.is_trial = False
        cm.save(update_fields=['is_enabled', 'is_trial', 'updated_at'])
        cls._audit(
            company, actor, 'disable_module', cm.id,
            f'Disabled module {mod.code}',
        )
        return cls._serialize_company_module(company, cm)

    @classmethod
    @transaction.atomic
    def start_trial(cls, company, module_code, *, actor=None, days=14):
        mod = cls._get_module(module_code)
        expires_at = timezone.now() + timedelta(days=days)
        cm, _ = CompanyModule.objects.update_or_create(
            company=company,
            module=mod,
            defaults={
                'is_enabled': True,
                'is_trial': True,
                'expires_at': expires_at,
                'from_plan': False,
            },
        )
        cls._audit(
            company, actor, 'trial_module', cm.id,
            f'Started {days}-day trial for {mod.code}',
        )
        return cls._serialize_company_module(company, cm)

    @classmethod
    @transaction.atomic
    def set_expiry(cls, company, module_code, expires_at, *, actor=None):
        mod = cls._get_module(module_code)
        cm = CompanyModule.objects.filter(company=company, module=mod).first()
        if not cm:
            raise ValueError(f'Module {module_code} not assigned.')
        cm.expires_at = expires_at
        cm.save(update_fields=['expires_at', 'updated_at'])
        cls._audit(
            company, actor, 'update_module', cm.id,
            f'Set expiry for {mod.code} to {expires_at}',
        )
        return cls._serialize_company_module(company, cm)

    @classmethod
    @transaction.atomic
    def set_usage_limits(cls, company, module_code, usage_limits, *, actor=None):
        mod = cls._get_module(module_code)
        cm = CompanyModule.objects.filter(company=company, module=mod).first()
        if not cm:
            raise ValueError(f'Module {module_code} not assigned.')
        cm.usage_limits = usage_limits or {}
        cm.save(update_fields=['usage_limits', 'updated_at'])
        cls._audit(
            company, actor, 'update_module', cm.id,
            f'Updated usage limits for {mod.code}',
        )
        return cls._serialize_company_module(company, cm)

    @classmethod
    @transaction.atomic
    def remove_module(cls, company, module_code, *, actor=None):
        mod = cls._get_module(module_code)
        cm = CompanyModule.objects.filter(company=company, module=mod).first()
        if not cm:
            return None
        cm_id = cm.id
        cm.delete()
        cls._audit(
            company, actor, 'remove_module', cm_id,
            f'Removed module {mod.code}',
        )
        return {'removed': module_code}

    @classmethod
    @transaction.atomic
    def bulk_assign(cls, company_ids, module_codes, *, actor=None, action='enable', trial_days=14):
        results = []
        for company_id in company_ids:
            company = Company.objects.filter(pk=company_id).first()
            if not company:
                continue
            for code in module_codes:
                try:
                    if action == 'enable':
                        row = cls.enable_module(company, code, actor=actor)
                    elif action == 'trial':
                        row = cls.start_trial(company, code, actor=actor, days=trial_days)
                    elif action == 'disable':
                        row = cls.disable_module(company, code, actor=actor)
                    else:
                        raise ValueError(f'Invalid action: {action}')
                    results.append({'company_id': company_id, 'module': code, 'ok': True, 'data': row})
                except ValueError as exc:
                    results.append({'company_id': company_id, 'module': code, 'ok': False, 'error': str(exc)})
        first_company = Company.objects.filter(pk__in=company_ids).first()
        if first_company:
            cls._audit(
                first_company,
                actor,
                'bulk_assign',
                0,
                f'Bulk {action} modules {module_codes} for {len(company_ids)} companies',
            )
        return results

    @classmethod
    def active_modules(cls, company):
        return [
            row for row in cls.company_modules(company)
            if row['is_accessible']
        ]
