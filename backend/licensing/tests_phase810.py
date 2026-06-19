from datetime import timedelta
from decimal import Decimal

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from auditlogs.models import AuditLog
from licensing.constants import INVOICE_STATUS_PAID
from licensing.customer_success_service import CustomerSuccessService
from licensing.models import (
    BillingInvoice,
    CompanySettings,
    CustomerSuccessEvent,
    CustomerSuccessProfile,
    RENEWAL_RISK_HIGH,
    RENEWAL_RISK_LOW,
    RENEWAL_RISK_MEDIUM,
    SubscriptionPlan,
    TenantSupportTicket,
)
from licensing.subscription_service import SubscriptionService


class CustomerSuccessServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='CS Co')
        CompanySettings.objects.create(company=self.company)
        self.plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={'name': 'Starter CS', 'monthly_price': 1000, 'sort_order': 1},
        )
        SubscriptionService.start_trial(self.company, plan=self.plan)
        self.superuser = CustomUser.objects.create_superuser(
            username='csowner', email='cs@t.com', password='pass1234',
        )

    def test_health_score_and_renewal_risk(self):
        user = CustomUser.objects.create_user(
            username='u1', password='pass1234', company=self.company,
            last_login=timezone.now(),
        )
        snap = CustomerSuccessService.company_snapshot(self.company)
        self.assertIn('health_score', snap)
        self.assertGreaterEqual(snap['health_score'], 0)
        self.assertLessEqual(snap['health_score'], 100)
        self.assertIn(snap['renewal_risk'], (RENEWAL_RISK_LOW, RENEWAL_RISK_MEDIUM, RENEWAL_RISK_HIGH))
        profile = CustomerSuccessProfile.objects.get(company=self.company)
        self.assertEqual(profile.health_score, snap['health_score'])
        self.assertIsNotNone(user)

    def test_high_risk_from_open_tickets(self):
        for i in range(3):
            TenantSupportTicket.objects.create(
                company=self.company,
                subject=f'Ticket {i}',
                description='Issue',
                status=TenantSupportTicket.STATUS_OPEN,
            )
        snap = CustomerSuccessService.company_snapshot(self.company)
        self.assertEqual(snap['renewal_risk'], RENEWAL_RISK_HIGH)

    def test_dashboard_and_alerts(self):
        TenantSupportTicket.objects.create(
            company=self.company,
            subject='Help',
            description='Need help',
            status=TenantSupportTicket.STATUS_OPEN,
        )
        dash = CustomerSuccessService.dashboard()
        self.assertEqual(dash['totals']['companies'], 1)
        self.assertGreaterEqual(dash['totals']['open_alerts'], 1)
        self.assertTrue(dash['renewal_alerts'])

    def test_timeline_merges_sources(self):
        CustomerSuccessEvent.objects.create(
            company=self.company,
            event_type=CustomerSuccessEvent.EVENT_MEETING,
            title='Kickoff',
            body='Intro call',
            created_by=self.superuser,
        )
        AuditLog.objects.create(
            company=self.company,
            module='licensing',
            action='enable_module',
            object_id=1,
            description='Enabled WhatsApp',
        )
        BillingInvoice.objects.create(
            company=self.company,
            invoice_number='INV-CS-001',
            amount=Decimal('999.00'),
            status=INVOICE_STATUS_PAID,
            paid_at=timezone.now(),
        )
        timeline = CustomerSuccessService.company_timeline(self.company)
        sources = {e['source'] for e in timeline}
        self.assertIn('cs_event', sources)
        self.assertIn('audit', sources)
        self.assertIn('billing', sources)

    def test_update_success_manager_and_notes(self):
        detail = CustomerSuccessService.update_company(
            self.company.id,
            actor=self.superuser,
            data={
                'success_manager_id': self.superuser.id,
                'meeting_notes': 'QBR scheduled',
                'renewal_date': (timezone.now() + timedelta(days=90)).date(),
            },
        )
        self.assertEqual(detail['success_manager']['id'], self.superuser.id)
        self.assertEqual(detail['meeting_notes'], 'QBR scheduled')
        self.assertTrue(
            CustomerSuccessEvent.objects.filter(
                company=self.company,
                event_type=CustomerSuccessEvent.EVENT_MEETING,
            ).exists(),
        )


class CustomerSuccessAPITests(APITestCase):
    def setUp(self):
        self.superuser = CustomUser.objects.create_superuser(
            username='owner', email='o@t.com', password='pass1234',
        )
        self.tenant = CustomUser.objects.create_user(
            username='tenant', password='pass1234',
        )
        self.company = Company.objects.create(name='API CS Co')
        CompanySettings.objects.create(company=self.company)
        plan, _ = SubscriptionPlan.objects.get_or_create(
            code='starter',
            defaults={'name': 'Starter API CS', 'monthly_price': 1000},
        )
        SubscriptionService.start_trial(self.company, plan=plan)

    def _owner_auth(self):
        token = RefreshToken.for_user(self.superuser)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_dashboard_requires_owner(self):
        r = self.client.get('/api/owner/customer-success/dashboard/')
        self.assertEqual(r.status_code, 401)
        token = RefreshToken.for_user(self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        r2 = self.client.get('/api/owner/customer-success/dashboard/')
        self.assertEqual(r2.status_code, 403)

    def test_dashboard_alerts_and_company(self):
        self._owner_auth()
        r = self.client.get('/api/owner/customer-success/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('companies', r.data)
        self.assertIn('totals', r.data)
        self.assertIn('renewal_alerts', r.data)

        r2 = self.client.get('/api/owner/customer-success/alerts/')
        self.assertEqual(r2.status_code, 200)
        self.assertIn('alerts', r2.data)

        r3 = self.client.get(f'/api/owner/customer-success/companies/{self.company.id}/')
        self.assertEqual(r3.status_code, 200)
        self.assertEqual(r3.data['company_id'], self.company.id)
        self.assertIn('timeline', r3.data)

        r4 = self.client.patch(
            f'/api/owner/customer-success/companies/{self.company.id}/',
            {'meeting_notes': 'Follow up next week'},
            format='json',
        )
        self.assertEqual(r4.status_code, 200)
        self.assertEqual(r4.data['meeting_notes'], 'Follow up next week')
