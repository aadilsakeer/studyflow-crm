from django.core.management.base import BaseCommand

from licensing.constants import MODULE_CATALOG
from licensing.models import Module, PlanModule, SubscriptionPlan


class Command(BaseCommand):

    help = "Seed licensing modules, SaaS plans, and plan-module mappings"

    def handle(self, *args, **options):

        module_map = {}
        for code, name in MODULE_CATALOG:
            mod, _ = Module.objects.update_or_create(
                code=code,
                defaults={'name': name, 'is_active': True},
            )
            module_map[code] = mod

        legacy = [
            ('Dashboard', 'dashboard'),
            ('Reports', 'reports'),
            ('Finance', 'finance'),
            ('Recruitment', 'recruitment'),
            ('Work Visa', 'workvisa'),
            ('Client Portal', 'clientportal'),
            ('Notifications', 'notifications'),
        ]
        for name, code in legacy:
            mod, _ = Module.objects.get_or_create(
                code=code,
                defaults={'name': name},
            )
            module_map[code] = mod

        plans = [
            {
                'name': 'Starter',
                'code': 'starter',
                'monthly_price': 4999,
                'yearly_price': 49999,
                'trial_days': 14,
                'max_users': 5,
                'max_leads': 500,
                'max_students': 100,
                'max_whatsapp_per_month': 200,
                'max_storage_mb': 1024,
                'sort_order': 1,
                'modules': ['crm', 'admissions', 'reports', 'dashboard'],
            },
            {
                'name': 'Growth',
                'code': 'growth',
                'monthly_price': 9999,
                'yearly_price': 99999,
                'trial_days': 14,
                'max_users': 20,
                'max_leads': 5000,
                'max_students': 1000,
                'max_whatsapp_per_month': 2000,
                'max_storage_mb': 10240,
                'sort_order': 2,
                'modules': [
                    'crm', 'admissions', 'studentportal', 'whatsapp',
                    'automation', 'knowledgebase', 'reports', 'dashboard',
                ],
            },
            {
                'name': 'Enterprise',
                'code': 'enterprise',
                'monthly_price': 19999,
                'yearly_price': 199999,
                'trial_days': 14,
                'max_users': None,
                'max_leads': None,
                'max_students': None,
                'max_whatsapp_per_month': None,
                'max_storage_mb': None,
                'sort_order': 3,
                'modules': list(module_map.keys()),
            },
            {
                'name': 'Custom',
                'code': 'custom',
                'monthly_price': 0,
                'yearly_price': 0,
                'trial_days': 30,
                'max_users': None,
                'max_leads': None,
                'max_students': None,
                'max_whatsapp_per_month': None,
                'max_storage_mb': None,
                'sort_order': 4,
                'modules': [],
            },
        ]

        for data in plans:
            module_codes = data.pop('modules')
            plan, _ = SubscriptionPlan.objects.update_or_create(
                code=data['code'],
                defaults=data,
            )
            for code in module_codes:
                if code in module_map:
                    PlanModule.objects.get_or_create(
                        plan=plan,
                        module=module_map[code],
                    )

        SubscriptionPlan.objects.filter(code='professional').update(
            is_active=False,
        )

        self.stdout.write(
            self.style.SUCCESS(
                'Module catalog + SaaS plans seeded successfully.',
            ),
        )
