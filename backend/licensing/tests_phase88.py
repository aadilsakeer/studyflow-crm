from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from licensing.models import CompanySettings, SubscriptionPlan
from licensing.subscription_service import SubscriptionService


class OwnerConsoleAPITests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='owner', email='owner@globvio.com', password='pass1234',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.admin).access_token}',
        )
        self.plan = SubscriptionPlan.objects.get_or_create(
            code='starter', defaults={'name': 'Starter', 'monthly_price': 4999},
        )[0]
        self.company = Company.objects.create(name='Tenant X', email='x@t.com')
        CompanySettings.objects.create(company=self.company)
        SubscriptionService.start_trial(self.company, plan=self.plan)

    def test_owner_dashboard(self):
        r = self.client.get('/api/owner/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('mrr', r.data['totals'])

    def test_company_list_and_deep_view(self):
        r = self.client.get('/api/owner/companies/')
        self.assertEqual(r.status_code, 200)
        r2 = self.client.get(f'/api/owner/companies/{self.company.id}/')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('audit_logs', r2.data)

    def test_suspend_and_impersonate(self):
        tenant_admin = CustomUser.objects.create_user(
            username='ta', email='ta@t.com', password='pass1234',
            company=self.company,
        )
        r = self.client.patch(
            f'/api/owner/companies/{self.company.id}/',
            {'action': 'suspend'}, format='json',
        )
        self.assertEqual(r.status_code, 200)
        r2 = self.client.post(
            f'/api/owner/companies/{self.company.id}/impersonate/',
            {'user_id': tenant_admin.id}, format='json',
        )
        self.assertEqual(r2.status_code, 200)
        self.assertIn('access', r2.data)

    def test_non_superuser_forbidden(self):
        user = CustomUser.objects.create_user(username='u', password='pass1234')
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(user).access_token}',
        )
        r = self.client.get('/api/owner/dashboard/')
        self.assertEqual(r.status_code, 403)
