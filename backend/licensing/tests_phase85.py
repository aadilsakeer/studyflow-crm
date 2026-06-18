from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from licensing.models import CompanySettings, SubscriptionPlan
from licensing.platform_service import PlatformOpsService
from licensing.subscription_service import SubscriptionService


class PlatformOpsServiceTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name='P1', code='p1', monthly_price=1000, sort_order=1,
        )
        self.company = Company.objects.create(name='Ops Co')
        CompanySettings.objects.create(company=self.company)
        SubscriptionService.start_trial(self.company, plan=self.plan)

    def test_suspend_and_extend_trial(self):
        PlatformOpsService.set_company_active(self.company.id, False)
        self.company.refresh_from_db()
        self.assertFalse(self.company.is_active)
        sub = PlatformOpsService.extend_trial(self.company.id, days=5)
        self.assertEqual(sub.status, 'trial')


class PlatformOpsAPITests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='super', email='s@t.com', password='pass1234',
        )
        token = RefreshToken.for_user(self.admin)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_operations_dashboard(self):
        r = self.client.get('/api/saas/admin/operations/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('monthly_revenue', r.data['totals'])
