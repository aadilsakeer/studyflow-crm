from datetime import date, time

from django.test import TestCase
from django.utils import timezone
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from hrm.models import Department, Employee, Shift
from hrm.owner_service import OwnerHRMService
from licensing.models import CompanySettings


class OwnerHRMServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='HR Co')
        CompanySettings.objects.create(company=self.company)
        self.dept = Department.objects.create(company=self.company, name='Engineering')
        self.shift = Shift.objects.create(
            company=self.company,
            name='Day',
            start_time=time(9, 0),
            end_time=time(18, 0),
            grace_minutes=15,
        )
        self.user = CustomUser.objects.create_user(
            username='emp1', password='pass1234', company=self.company,
        )
        self.owner = CustomUser.objects.create_superuser(
            username='hrowner', email='hr@t.com', password='pass1234',
        )
        self.employee = Employee.objects.create(
            company=self.company,
            user=self.user,
            employee_code='E001',
            full_name='Test Employee',
            department=self.dept,
            designation='Developer',
            shift=self.shift,
            salary_structure={'basic': 50000},
        )

    def test_employee_directory(self):
        rows = OwnerHRMService.list_employees(company_id=self.company.id)
        self.assertEqual(len(rows), 1)
        detail = OwnerHRMService.get_employee(self.employee.id)
        self.assertEqual(detail['designation'], 'Developer')

    def test_check_in_out_with_gps(self):
        att = OwnerHRMService.check_in(
            actor=self.owner,
            employee_id=self.employee.id,
            latitude='12.9716000',
            longitude='77.5946000',
        )
        self.assertIsNotNone(att['check_in_at'])
        out = OwnerHRMService.check_out(
            actor=self.owner,
            employee_id=self.employee.id,
            latitude='12.9716000',
            longitude='77.5946000',
        )
        self.assertIsNotNone(out['check_out_at'])

    def test_leave_apply_approve(self):
        leave = OwnerHRMService.apply_leave(
            actor=self.owner,
            data={
                'employee_id': self.employee.id,
                'start_date': date.today(),
                'end_date': date.today(),
                'leave_type': 'annual',
                'reason': 'Personal',
            },
        )
        self.assertEqual(leave['status'], 'pending')
        approved = OwnerHRMService.review_leave(
            actor=self.owner,
            leave_id=leave['id'],
            status='approved',
        )
        self.assertEqual(approved['status'], 'approved')

    def test_payroll_and_assets(self):
        payroll = OwnerHRMService.create_payroll(
            actor=self.owner,
            data={
                'employee_id': self.employee.id,
                'month': 'June',
                'year': timezone.now().year,
                'basic_salary': 50000,
                'deductions': 5000,
            },
        )
        self.assertIn('payslip', payroll)
        updated = OwnerHRMService.update_payroll_status(
            actor=self.owner,
            payroll_id=payroll['id'],
            payment_status='paid',
        )
        self.assertEqual(updated['payment_status'], 'paid')

        asset = OwnerHRMService.assign_asset(
            actor=self.owner,
            data={
                'employee_id': self.employee.id,
                'asset_type': 'laptop',
                'asset_name': 'MacBook Pro',
                'serial_number': 'SN-123',
            },
        )
        self.assertEqual(asset['status'], 'assigned')
        history = OwnerHRMService.asset_history(serial_number='SN-123')
        self.assertEqual(len(history), 1)


class OwnerHRMAPITests(APITestCase):
    def setUp(self):
        self.owner = CustomUser.objects.create_superuser(
            username='owner', email='o@t.com', password='pass1234',
        )
        self.company = Company.objects.create(name='API HR Co')
        CompanySettings.objects.create(company=self.company)
        self.user = CustomUser.objects.create_user(
            username='staff', password='pass1234', company=self.company,
        )
        self.employee = Employee.objects.create(
            company=self.company,
            user=self.user,
            employee_code='E100',
            full_name='API Staff',
            designation='Analyst',
        )

    def _auth(self):
        token = RefreshToken.for_user(self.owner)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_owner_hrms_flow(self):
        self._auth()
        r = self.client.get('/api/owner/hrms/dashboard/')
        self.assertEqual(r.status_code, 200)

        r2 = self.client.get('/api/owner/hrms/employees/')
        self.assertEqual(r2.status_code, 200)

        r3 = self.client.post(
            '/api/owner/hrms/attendance/check-in/',
            {'employee_id': self.employee.id, 'latitude': '12.97', 'longitude': '77.59'},
            format='json',
        )
        self.assertEqual(r3.status_code, 201)

        r4 = self.client.post(
            '/api/owner/hrms/leaves/',
            {
                'employee_id': self.employee.id,
                'start_date': str(date.today()),
                'end_date': str(date.today()),
                'reason': 'Test',
            },
            format='json',
        )
        self.assertEqual(r4.status_code, 201)

        r5 = self.client.patch(
            f'/api/owner/hrms/leaves/{r4.data["id"]}/',
            {'status': 'approved'},
            format='json',
        )
        self.assertEqual(r5.status_code, 200)

        r6 = self.client.post(
            '/api/owner/hrms/payroll/',
            {
                'employee_id': self.employee.id,
                'month': 'June',
                'year': 2026,
                'basic_salary': '40000',
                'deductions': '2000',
            },
            format='json',
        )
        self.assertEqual(r6.status_code, 201)

        r7 = self.client.post(
            '/api/owner/hrms/assets/',
            {
                'employee_id': self.employee.id,
                'asset_type': 'phone',
                'asset_name': 'iPhone',
                'serial_number': 'PH-1',
            },
            format='json',
        )
        self.assertEqual(r7.status_code, 201)
