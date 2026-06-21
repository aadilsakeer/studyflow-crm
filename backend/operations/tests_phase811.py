from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from auditlogs.models import AuditLog
from licensing.models import CompanySettings, TenantSupportTicket
from operations.constants import (
    STATUS_IN_PROGRESS,
    TICKET_TYPE_BUG,
    TICKET_TYPE_ESCALATION,
)
from operations.models import InternalComment, InternalTeamMember, InternalTicket
from operations.service import InternalOperationsService


class InternalOperationsServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Ops Co')
        CompanySettings.objects.create(company=self.company)
        self.owner = CustomUser.objects.create_superuser(
            username='opsowner', email='ops@t.com', password='pass1234',
        )
        InternalTeamMember.objects.create(
            user=self.owner, team='developer', weekly_capacity=8,
        )

    def test_create_assign_comment(self):
        ticket = InternalOperationsService.create_ticket(
            actor=self.owner,
            data={
                'ticket_type': TICKET_TYPE_BUG,
                'title': 'Login broken',
                'description': 'Users cannot login',
                'company_id': self.company.id,
            },
        )
        self.assertEqual(ticket['title'], 'Login broken')
        updated = InternalOperationsService.assign_ticket(
            ticket_id=ticket['id'],
            actor=self.owner,
            assignee_id=self.owner.id,
            status=STATUS_IN_PROGRESS,
        )
        self.assertEqual(updated['assignee']['id'], self.owner.id)
        comment = InternalOperationsService.add_comment(
            ticket_id=ticket['id'],
            actor=self.owner,
            body='Investigating root cause',
        )
        self.assertIn('Investigating', comment['body'])

    def test_escalate_support_ticket(self):
        support = TenantSupportTicket.objects.create(
            company=self.company,
            subject='Billing issue',
            description='Invoice wrong',
        )
        ticket = InternalOperationsService.escalate_support_ticket(
            support_ticket_id=support.id,
            actor=self.owner,
            assignee_id=self.owner.id,
        )
        self.assertEqual(ticket['ticket_type'], TICKET_TYPE_ESCALATION)
        self.assertEqual(ticket['source_support_ticket_id'], support.id)
        self.assertTrue(
            InternalComment.objects.filter(ticket_id=ticket['id']).exists(),
        )
        self.assertTrue(
            AuditLog.objects.filter(
                company=self.company,
                action='escalate_support_ticket',
            ).exists(),
        )

    def test_workload_dashboard_and_board(self):
        InternalOperationsService.create_ticket(
            actor=self.owner,
            data={'title': 'Open bug', 'description': 'x', 'company_id': self.company.id},
        )
        dash = InternalOperationsService.workload_dashboard()
        self.assertGreaterEqual(dash['totals']['open_tickets'], 1)
        board = InternalOperationsService.board()
        self.assertIn('columns', board)


class InternalOperationsAPITests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_superuser(
            username='owner', email='o@t.com', password='pass1234',
        )
        self.tenant = CustomUser.objects.create_user(
            username='tenant', password='pass1234',
        )
        self.company = Company.objects.create(name='API Ops Co')
        CompanySettings.objects.create(company=self.company)
        InternalTeamMember.objects.create(user=self.owner, team='support')

    def _owner_auth(self):
        token = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_owner_operations_apis(self):
        self._owner_auth()
        r = self.client.get('/api/owner/operations/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('totals', r.data)

        r2 = self.client.post(
            '/api/owner/operations/tickets/',
            {
                'ticket_type': 'bug',
                'title': 'API test ticket',
                'description': 'From test',
                'company_id': self.company.id,
            },
            format='json',
        )
        self.assertEqual(r2.status_code, 201)
        tid = r2.data['id']

        r3 = self.client.patch(
            f'/api/owner/operations/tickets/{tid}/',
            {'assignee_id': self.owner.id, 'status': 'in_progress'},
            format='json',
        )
        self.assertEqual(r3.status_code, 200)

        r4 = self.client.post(
            f'/api/owner/operations/tickets/{tid}/comments/',
            {'body': 'Working on it'},
            format='json',
        )
        self.assertEqual(r4.status_code, 201)

        r5 = self.client.get('/api/owner/operations/board/')
        self.assertEqual(r5.status_code, 200)

        support = TenantSupportTicket.objects.create(
            company=self.company,
            subject='Help',
            description='Need help',
        )
        r6 = self.client.post(
            '/api/owner/operations/tickets/escalate/',
            {'support_ticket_id': support.id},
            format='json',
        )
        self.assertEqual(r6.status_code, 201)
        self.assertEqual(r6.data['ticket_type'], TICKET_TYPE_ESCALATION)

    def test_requires_superuser(self):
        token = RefreshToken.for_user(self.tenant)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')
        r = self.client.get('/api/owner/operations/dashboard/')
        self.assertEqual(r.status_code, 403)
