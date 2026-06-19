from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import PERM_BILLING_VIEW, ROLE_ADMIN
from accounts.models import Company, CustomUser, Permission, Role, RolePermission
from auditlogs.models import AuditLog
from licensing.models import CompanyModule, CompanySettings, Module, SubscriptionPlan
from licensing.module_service import ModuleLicensingService
from licensing.services import ModuleAccessService
from licensing.subscription_service import SubscriptionService


class ModuleLicensingServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Mod Co')
        CompanySettings.objects.create(company=self.company)
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter Mod Test',
                'monthly_price': 1000,
                'sort_order': 1,
            },
        )
        SubscriptionService.start_trial(self.company, plan=self.plan)
        self.mod, _ = Module.objects.get_or_create(
            code='whatsapp', defaults={'name': 'WhatsApp'},
        )

    def test_enable_disable_and_audit(self):
        admin = CustomUser.objects.create_user(
            username='admin', password='pass1234', company=self.company,
        )
        ModuleLicensingService.enable_module(
            self.company, 'whatsapp', actor=admin,
        )
        self.assertTrue(
            CompanyModule.objects.filter(
                company=self.company, module=self.mod, is_enabled=True,
            ).exists(),
        )
        self.assertTrue(
            AuditLog.objects.filter(
                company=self.company, action='enable_module',
            ).exists(),
        )
        ModuleLicensingService.disable_module(
            self.company, 'whatsapp', actor=admin,
        )
        cm = CompanyModule.objects.get(company=self.company, module=self.mod)
        self.assertFalse(cm.is_enabled)

    def test_trial_expiry_blocks_access(self):
        ModuleLicensingService.start_trial(
            self.company, 'whatsapp', days=1,
        )
        self.assertTrue(ModuleAccessService.has_access(self.company, 'whatsapp'))
        cm = CompanyModule.objects.get(company=self.company, module=self.mod)
        cm.expires_at = timezone.now() - timedelta(hours=1)
        cm.save(update_fields=['expires_at'])
        self.assertFalse(ModuleAccessService.has_access(self.company, 'whatsapp'))

    def test_bulk_assign(self):
        c2 = Company.objects.create(name='Co 2')
        ModuleLicensingService.bulk_assign(
            [self.company.id, c2.id], ['whatsapp'], action='enable',
        )
        self.assertEqual(
            CompanyModule.objects.filter(module=self.mod, is_enabled=True).count(),
            2,
        )


class ModuleLicensingAPITests(APITestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            username='owner', email='o@t.com', password='pass1234',
        )
        self.company = Company.objects.create(name='API Co')
        CompanySettings.objects.create(company=self.company)
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter API Test',
                'monthly_price': 1000,
            },
        )
        SubscriptionService.start_trial(self.company, plan=self.plan)
        Module.objects.get_or_create(code='whatsapp', defaults={'name': 'WhatsApp'})
        Module.objects.get_or_create(code='ai', defaults={'name': 'AI'})
        role, _ = Role.objects.get_or_create(name=ROLE_ADMIN)
        perm, _ = Permission.objects.get_or_create(
            code=PERM_BILLING_VIEW,
            defaults={'name': PERM_BILLING_VIEW},
        )
        RolePermission.objects.get_or_create(role=role, permission=perm)
        self.tenant_user = CustomUser.objects.create_user(
            username='tenant', password='pass1234',
            company=self.company, role=role,
        )

    def _owner_auth(self):
        token = RefreshToken.for_user(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def _tenant_auth(self):
        token = RefreshToken.for_user(self.tenant_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_owner_catalog_and_company_modules(self):
        self._owner_auth()
        r = self.client.get('/api/owner/modules/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('catalog', r.data)
        r2 = self.client.post(
            f'/api/owner/companies/{self.company.id}/modules/',
            {'action': 'enable', 'module_code': 'whatsapp'},
            format='json',
        )
        self.assertEqual(r2.status_code, 200)
        r3 = self.client.get(f'/api/owner/companies/{self.company.id}/modules/')
        self.assertEqual(r3.status_code, 200)
        self.assertTrue(any(m['code'] == 'whatsapp' for m in r3.data))

    def test_bulk_assign_api(self):
        self._owner_auth()
        c2 = Company.objects.create(name='Bulk Co')
        r = self.client.post(
            '/api/owner/modules/bulk-assign/',
            {
                'company_ids': [self.company.id, c2.id],
                'module_codes': ['ai'],
                'action': 'trial',
                'trial_days': 7,
            },
            format='json',
        )
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['results']), 2)

    def test_tenant_modules_api(self):
        ModuleLicensingService.enable_module(self.company, 'whatsapp')
        self._tenant_auth()
        r = self.client.get('/api/saas/modules/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('active', r.data)

    def test_deep_view_includes_modules(self):
        self._owner_auth()
        ModuleLicensingService.enable_module(self.company, 'whatsapp')
        r = self.client.get(f'/api/owner/companies/{self.company.id}/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('modules', r.data)
