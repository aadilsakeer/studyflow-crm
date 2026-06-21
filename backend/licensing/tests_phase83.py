from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import (
    PERM_BILLING_MANAGE,
    PERM_BILLING_VIEW,
    PERM_SUPPORT_ADD,
    PERM_SUPPORT_VIEW,
    ROLE_ADMIN,
)
from accounts.models import Company, CustomUser, Permission, Role, RolePermission
from licensing.models import (
    BillingInvoice,
    CompanySettings,
    CompanySubscription,
    SubscriptionPlan,
    TenantSupportTicket,
)
from licensing.subscription_service import SubscriptionService
from licensing.support_service import SupportDeskService


class Phase83SupportTests(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name='Pro',
            code='pro',
            monthly_price=9999,
            trial_days=14,
        )
        self.company = Company.objects.create(name='Support Co')
        CompanySettings.objects.create(company=self.company)
        SubscriptionService.start_trial(self.company, plan=self.plan)
        self.role = Role.objects.create(name=ROLE_ADMIN)
        self.user = CustomUser.objects.create_user(
            username='admin',
            password='pass1234',
            company=self.company,
            role=self.role,
        )

    def test_create_ticket_with_sla(self):
        ticket = SupportDeskService.create_ticket(
            company=self.company,
            user=self.user,
            subject='Billing issue',
            description='Need help upgrading',
            priority=TenantSupportTicket.PRIORITY_HIGH,
        )
        self.assertEqual(ticket.status, TenantSupportTicket.STATUS_OPEN)
        self.assertIsNotNone(ticket.sla_due_at)
        self.assertEqual(ticket.messages.count(), 1)

    def test_renew_period_creates_invoice(self):
        SubscriptionService.renew_period(
            self.company,
            period_start=timezone.now(),
            period_end=timezone.now() + timedelta(days=30),
            amount=9999,
            billing_cycle='monthly',
            provider='stripe',
            provider_invoice_id='inv_test',
        )
        self.assertEqual(
            BillingInvoice.objects.filter(company=self.company).count(),
            1,
        )


class Phase83APITests(APITestCase):
    def setUp(self):
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={
                'name': 'Starter Test',
                'monthly_price': 4999,
                'trial_days': 14,
                'sort_order': 1,
            },
        )
        self.company = Company.objects.create(name='API Co')
        CompanySettings.objects.create(company=self.company)
        SubscriptionService.start_trial(self.company, plan=self.plan)

        self.role = Role.objects.create(name=ROLE_ADMIN)
        for code in (
            PERM_BILLING_VIEW,
            PERM_BILLING_MANAGE,
            PERM_SUPPORT_ADD,
            PERM_SUPPORT_VIEW,
        ):
            perm, _ = Permission.objects.get_or_create(
                code=code,
                defaults={'name': code},
            )
            RolePermission.objects.get_or_create(role=self.role, permission=perm)

        self.user = CustomUser.objects.create_user(
            username='billing',
            password='pass1234',
            company=self.company,
            role=self.role,
        )
        token = RefreshToken.for_user(self.user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token.access_token}',
        )

    def test_support_ticket_create_and_list(self):
        create = self.client.post(
            '/api/saas/support/tickets/',
            {
                'subject': 'Help',
                'description': 'Need assistance',
                'priority': 'normal',
            },
            format='json',
        )
        self.assertEqual(create.status_code, 201)

        listing = self.client.get('/api/saas/support/tickets/')
        self.assertEqual(listing.status_code, 200)
        self.assertEqual(len(listing.data), 1)

    def test_billing_payments_list(self):
        response = self.client.get('/api/saas/billing/payments/')
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.data, list)

    def test_change_plan_during_trial(self):
        pro = SubscriptionPlan.objects.create(
            name='Professional',
            code='professional',
            monthly_price=9999,
        )
        response = self.client.post(
            '/api/saas/subscription/change-plan/',
            {'plan_code': pro.code},
            format='json',
        )
        self.assertEqual(response.status_code, 200)
        sub = CompanySubscription.objects.get(company=self.company)
        self.assertEqual(sub.plan_id, pro.id)

    def test_settings_include_branding_fields(self):
        response = self.client.get('/api/saas/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('brand_logo_url', response.data)
        self.assertIn('brand_favicon_url', response.data)
