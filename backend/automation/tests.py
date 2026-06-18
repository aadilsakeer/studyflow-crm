from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from accounts.models import Company, CustomUser

from admissions.models import Application, OfferLetter, Student, StudentDocument, VisaCase
from deadlines.models import Deadline
from leads.models import FollowUp, Lead
from notifications.models import Notification

from .reminder_service import run_company_reminders


class WorkflowReminderTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Auto Co')
        self.user = CustomUser.objects.create_user(
            username='counsellor1',
            password='pass1234',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Auto',
            last_name='Lead',
            phone='9222222222',
            assigned_to=self.user,
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-AUTO-1',
            assigned_counselor=self.user,
        )

    def test_follow_up_reminder_creates_notification(self):
        FollowUp.objects.create(
            lead=self.lead,
            assigned_to=self.user,
            follow_up_date=timezone.now() - timedelta(hours=1),
        )

        summary = run_company_reminders(self.company)

        self.assertEqual(summary['follow_up'], 1)
        self.assertEqual(Notification.objects.count(), 1)

    def test_missing_document_reminder(self):
        StudentDocument.objects.create(
            company=self.company,
            student=self.student,
            document_type='passport',
            status='requested',
        )

        summary = run_company_reminders(self.company)

        self.assertEqual(summary['missing_document'], 1)

    def test_offer_expiry_reminder(self):
        application = Application.objects.create(
            student=self.student,
            university_name='Test U',
            course_name='CS',
            intake='Fall 2026',
        )
        OfferLetter.objects.create(
            company=self.company,
            student=self.student,
            application=application,
            university='Test U',
            course='CS',
            offer_number='OFF-AUTO-1',
            expiry_date=timezone.localdate() + timedelta(days=3),
        )

        summary = run_company_reminders(self.company)

        self.assertEqual(summary['offer_expiry'], 1)

    def test_visa_appointment_reminder(self):
        VisaCase.objects.create(
            company=self.company,
            student=self.student,
            country='Canada',
            appointment_date=timezone.localdate() + timedelta(days=2),
        )

        summary = run_company_reminders(self.company)

        self.assertEqual(summary['visa_appointment'], 1)

    def test_application_deadline_reminder(self):
        Deadline.objects.create(
            student=self.student,
            title='Submit application',
            due_date=timezone.localdate() + timedelta(days=5),
        )

        summary = run_company_reminders(self.company)

        self.assertEqual(summary['application_deadline'], 1)

    def test_duplicate_alerts_not_sent_twice(self):
        FollowUp.objects.create(
            lead=self.lead,
            assigned_to=self.user,
            follow_up_date=timezone.now() - timedelta(hours=1),
        )

        run_company_reminders(self.company)
        run_company_reminders(self.company)

        self.assertEqual(Notification.objects.count(), 1)
