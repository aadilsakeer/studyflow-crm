from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import PERM_SETTINGS_MANAGE, ROLE_ADMIN
from accounts.models import Company, CustomUser, Permission, Role, RolePermission
from licensing.models import CompanySettings, SubscriptionPlan
from licensing.subscription_service import SubscriptionService


class BootstrapOwnerTests(TestCase):
    def test_bootstrap_owner_creates_superuser(self):
        out = StringIO()
        call_command('bootstrap_owner', stdout=out)
        user = CustomUser.objects.get(username='owner')
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.check_password('Owner@123'))
        self.assertIn('owner@globvio.local', out.getvalue())


class OnboardingAPITests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_superuser(
            username='owner', email='owner@globvio.local', password='Owner@123',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.owner).access_token}',
        )
        SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={'name': 'Starter', 'monthly_price': 1000, 'sort_order': 1},
        )

    def test_onboard_tenant_returns_credentials(self):
        r = self.client.post('/api/owner/onboard/', {
            'name': 'New Co',
            'email': 'co@test.com',
            'admin_email': 'admin@test.com',
            'plan_code': 'starter',
            'module_codes': ['whatsapp'],
        }, format='json')
        self.assertEqual(r.status_code, 201)
        self.assertIn('temporary_password', r.data)
        self.assertTrue(Company.objects.filter(name='New Co').exists())

    def test_owner_reset_password(self):
        company = Company.objects.create(name='PW Co')
        CompanySettings.objects.create(company=company)
        SubscriptionService.start_trial(company)
        role = Role.objects.create(name=ROLE_ADMIN)
        user = CustomUser.objects.create_user(
            username='admin@test.com', email='admin@test.com',
            password='oldpass12', company=company, role=role,
        )
        r = self.client.post(f'/api/owner/users/{user.id}/', {
            'action': 'reset_password',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('temporary_password', r.data)

    def test_tenant_admin_reset_staff_password(self):
        company = Company.objects.create(name='Staff Co')
        role = Role.objects.create(name=ROLE_ADMIN)
        perm, _ = Permission.objects.get_or_create(
            code=PERM_SETTINGS_MANAGE, defaults={'name': PERM_SETTINGS_MANAGE},
        )
        RolePermission.objects.get_or_create(role=role, permission=perm)
        admin = CustomUser.objects.create_user(
            username='admin', password='pass1234', company=company, role=role,
        )
        staff = CustomUser.objects.create_user(
            username='staff1', password='pass1234', company=company,
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(admin).access_token}',
        )
        r = self.client.post(f'/api/staff/{staff.id}/', {
            'action': 'reset_password',
        }, format='json')
        self.assertEqual(r.status_code, 200)
        self.assertIn('temporary_password', r.data)
