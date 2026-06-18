from decimal import Decimal

from django.test import TestCase

from accounts.models import Company, CustomUser

from admissions.models import Application, OfferLetter, Student, VisaCase
from finance.models import Payment
from leads.models import Lead, LeadSource

from .advanced_analytics import AdvancedReportService


class AdvancedReportServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Report Co')
        self.user = CustomUser.objects.create_user(
            username='reportadmin',
            password='pass1234',
            company=self.company,
        )
        self.source = LeadSource.objects.create(name='Website')
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Riya',
            last_name='Shah',
            phone='9111111111',
            status='converted',
            source=self.source,
            assigned_to=self.user,
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-RPT-1',
            destination_country='Canada',
        )
        Payment.objects.create(
            company=self.company,
            student=self.student,
            amount=Decimal('50000'),
            status='paid',
            payment_type='consultancy_fee',
        )
        application = Application.objects.create(
            student=self.student,
            university_name='Test University',
            course_name='Computer Science',
            intake='Fall 2026',
        )
        OfferLetter.objects.create(
            company=self.company,
            student=self.student,
            application=application,
            university='Test University',
            course='Computer Science',
            offer_number='OFF-001',
            status='accepted',
        )
        VisaCase.objects.create(
            company=self.company,
            student=self.student,
            country='Canada',
            status='approved',
        )

    def test_advanced_reports_structure(self):
        data = AdvancedReportService.get_reports(
            self.company,
            'all',
        )

        self.assertIn('lead_source_roi', data)
        self.assertIn('offer_conversion', data)
        self.assertIn('visa_success', data)
        self.assertEqual(data['offer_conversion']['offers_accepted'], 1)
        self.assertEqual(data['visa_success']['visas_approved'], 1)

    def test_export_helpers(self):
        from .export_utils import export_reports_csv, export_reports_xlsx

        reports = AdvancedReportService.get_reports(
            self.company,
            'all',
        )

        csv_data = export_reports_csv(reports)
        xlsx_data = export_reports_xlsx(reports)

        self.assertIn('Lead Source ROI', csv_data)
        self.assertTrue(len(xlsx_data) > 100)
