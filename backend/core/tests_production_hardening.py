from decimal import Decimal

from django.test import TestCase
from rest_framework.test import APITestCase, APIRequestFactory
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import ALL_PERMISSIONS, ROLE_ADMIN, ROLE_PERMISSIONS
from accounts.models import Company, CustomUser, Permission, Role, RolePermission
from admissions.models import Student
from auditlogs.models import AuditLog
from finance.models import Payment
from finance.serializers import InvoiceSerializer, RefundSerializer
from leads.conversion_service import convert_lead_to_student
from leads.models import FollowUp, Lead
from licensing.models import CompanyModule, Module


class ProductionHardeningTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Hard Co')
        self.other = Company.objects.create(name='Other Co')
        self.user = CustomUser.objects.create_user(
            username='hardadmin',
            password='pass1234',
            company=self.company,
        )
        self.other_user = CustomUser.objects.create_user(
            username='otheruser',
            password='pass1234',
            company=self.other,
        )
        self.other_student = Student.objects.create(
            company=self.other,
            lead=Lead.objects.create(
                company=self.other,
                first_name='O',
                last_name='L',
                phone='9111111111',
            ),
            student_id='STU-OTHER-1',
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Convert',
            last_name='Me',
            phone='9222222222',
            status='interested',
        )
        self.payment = Payment.objects.create(
            company=self.other,
            student=self.other_student,
            amount=Decimal('1000'),
            status='paid',
            payment_type='consultancy_fee',
        )

    def test_conversion_creates_audit_log(self):
        convert_lead_to_student(self.lead, self.user)

        self.assertTrue(
            AuditLog.objects.filter(
                company=self.company,
                module='Admissions',
                action='create',
            ).exists(),
        )

    def test_payment_rejects_cross_tenant_student(self):
        from finance.serializers import PaymentSerializer

        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.user

        serializer = PaymentSerializer(
            data={
                'student': self.other_student.id,
                'amount': '1000',
                'status': 'paid',
                'payment_type': 'consultancy_fee',
            },
            context={'request': request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('student', serializer.errors)

    def test_refund_rejects_cross_tenant_payment(self):
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.user

        serializer = RefundSerializer(
            data={
                'payment': self.payment.id,
                'amount': '100',
                'reason': 'test',
                'status': 'pending',
            },
            context={'request': request},
        )

        self.assertFalse(serializer.is_valid())
        self.assertIn('payment', serializer.errors)

    def test_invoice_rejects_cross_tenant_student(self):
        factory = APIRequestFactory()
        request = factory.post('/')
        request.user = self.user

        serializer = InvoiceSerializer(
            data={
                'student': self.other_student.id,
                'payment': self.payment.id,
                'invoice_date': '2026-06-01',
                'amount': '1000',
                'status': 'draft',
            },
            context={'request': request},
        )

        self.assertFalse(serializer.is_valid())


class TenantIsolationAPITests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Tenant A')
        self.other = Company.objects.create(name='Tenant B')

        admin_role = Role.objects.create(name=ROLE_ADMIN)
        perm_map = {
            code: Permission.objects.create(code=code, name=name)
            for code, name in ALL_PERMISSIONS
        }
        for code in ROLE_PERMISSIONS[ROLE_ADMIN]:
            RolePermission.objects.create(
                role=admin_role,
                permission=perm_map[code],
            )

        self.user = CustomUser.objects.create_user(
            username='tenadmin',
            password='pass1234',
            company=self.company,
            role=admin_role,
        )
        self.other_lead = Lead.objects.create(
            company=self.other,
            first_name='Secret',
            last_name='Lead',
            phone='9333333333',
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Mine',
            last_name='Lead',
            phone='9444444444',
        )

        finance_module, _ = Module.objects.get_or_create(
            code='finance',
            defaults={'name': 'Finance'},
        )
        CompanyModule.objects.get_or_create(
            company=self.company,
            module=finance_module,
            defaults={'is_enabled': True},
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token.access_token}',
        )

    def test_leads_list_tenant_isolated(self):
        self._auth(self.user)
        response = self.client.get('/api/leads/')
        phones = [row['phone'] for row in response.data['results']]
        self.assertIn('9444444444', phones)
        self.assertNotIn('9333333333', phones)

    def test_cannot_update_other_tenant_lead(self):
        self._auth(self.user)
        response = self.client.patch(
            f'/api/leads/{self.other_lead.id}/',
            {'remarks': 'hack'},
            format='json',
        )
        self.assertIn(response.status_code, (403, 404))

    def test_lead_create_logs_audit(self):
        self._auth(self.user)
        response = self.client.post(
            '/api/leads/',
            {
                'first_name': 'New',
                'last_name': 'Lead',
                'phone': '9555555555',
                'status': 'new',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            AuditLog.objects.filter(
                company=self.company,
                module='Leads',
                action='create',
            ).exists(),
        )

    def test_finance_blocked_without_module(self):
        CompanyModule.objects.filter(
            company=self.company,
            module__code='finance',
        ).delete()

        self._auth(self.user)
        response = self.client.get('/api/finance/payments/')
        self.assertEqual(response.status_code, 403)

    def test_followup_create_logs_audit(self):
        self._auth(self.user)
        response = self.client.post(
            '/api/followups/',
            {
                'lead': self.lead.id,
                'follow_up_date': '2026-06-20T10:00:00Z',
                'notes': 'Call back',
            },
            format='json',
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(
            AuditLog.objects.filter(
                company=self.company,
                module='FollowUps',
                action='create',
            ).exists(),
        )
