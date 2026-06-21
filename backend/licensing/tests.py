from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase

from accounts.models import Company, CustomUser
from leads.models import Lead

from .constants import LIMIT_LEADS, SUBSCRIPTION_STATUS_TRIAL
from .exceptions import LimitExceededError
from .models import (
    CompanySettings,
    CompanySubscription,
    SubscriptionPlan,
)
from .subscription_service import OnboardingService, SubscriptionService
from .usage_service import UsageLimitService


class SaasFoundationTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            code='test',
            monthly_price=1000,
            max_leads=2,
            max_students=1,
            max_users=2,
            trial_days=7,
        )
        self.company = Company.objects.create(name='SaaS Co')
        CompanySettings.objects.create(company=self.company)
        SubscriptionService.start_trial(self.company, plan=self.plan)

    def test_trial_subscription_usable(self):
        sub = CompanySubscription.objects.get(company=self.company)
        self.assertEqual(sub.status, SUBSCRIPTION_STATUS_TRIAL)
        self.assertTrue(sub.is_usable())

    def test_lead_limit_enforced(self):
        Lead.objects.create(
            company=self.company,
            first_name='A',
            last_name='B',
            phone='9000000001',
        )
        Lead.objects.create(
            company=self.company,
            first_name='C',
            last_name='D',
            phone='9000000002',
        )

        with self.assertRaises(LimitExceededError):
            UsageLimitService.check(self.company, LIMIT_LEADS)

    def test_onboarding_creates_tenant(self):
        company, user = OnboardingService.register_tenant(
            company_name='New Consultancy',
            admin_email='owner@test.com',
            admin_password='securepass123',
        )
        self.assertTrue(
            CompanySubscription.objects.filter(company=company).exists(),
        )
        self.assertTrue(
            CompanySettings.objects.filter(company=company).exists(),
        )
        self.assertEqual(user.company_id, company.id)

    def test_expired_trial_not_usable(self):
        sub = CompanySubscription.objects.get(company=self.company)
        sub.trial_ends_at = timezone.now() - timedelta(days=1)
        sub.save()
        self.assertFalse(sub.is_usable())


class SaasAPITests(APITestCase):
    def test_public_plan_list(self):
        SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter',
                'monthly_price': 4999,
                'is_active': True,
            },
        )
        response = self.client.get('/api/saas/plans/')
        self.assertEqual(response.status_code, 200)
        self.assertGreaterEqual(len(response.data), 1)

    def test_onboarding_register(self):
        SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter',
                'monthly_price': 4999,
                'is_active': True,
                'sort_order': 1,
            },
        )
        response = self.client.post(
            '/api/saas/onboard/register/',
            {
                'company_name': 'Globvio Test',
                'admin_email': 'saas@test.com',
                'admin_password': 'testpass1234',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            CustomUser.objects.filter(email='saas@test.com').exists(),
        )
