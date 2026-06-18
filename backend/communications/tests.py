from django.test import TestCase
from django.utils import timezone

from accounts.models import Company, CustomUser

from admissions.models import Student

from leads.models import CallLog, Lead

from communications.history_service import get_communication_history
from communications.models import CommunicationNote, EmailLog, WhatsAppLog


class CommunicationHistoryTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            name='Comm Co',
        )
        self.user = CustomUser.objects.create_user(
            username='commuser',
            password='pass12345',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Comm',
            last_name='Lead',
            phone='9111111111',
            email='comm@example.com',
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-COMM-1',
        )

    def test_unified_history_includes_all_types(self):
        CallLog.objects.create(
            lead=self.lead,
            called_by=self.user,
            outcome='Answered',
            notes='Discussed intake',
        )

        CommunicationNote.objects.create(
            company=self.company,
            lead=self.lead,
            author=self.user,
            content='Prefers UK universities',
        )

        EmailLog.objects.create(
            company=self.company,
            lead=self.lead,
            logged_by=self.user,
            recipient_email='comm@example.com',
            subject='Welcome',
            body='Thanks for your interest',
            sent_at=timezone.now(),
        )

        WhatsAppLog.objects.create(
            company=self.company,
            lead=self.lead,
            logged_by=self.user,
            contact_number='9111111111',
            message='Sent brochure',
        )

        events = get_communication_history(
            company=self.company,
            lead=self.lead,
        )

        types = {event['type'] for event in events}

        self.assertEqual(
            types,
            {'call', 'note', 'email', 'whatsapp'},
        )
        self.assertEqual(len(events), 4)

    def test_student_scoped_history(self):
        CommunicationNote.objects.create(
            company=self.company,
            student=self.student,
            author=self.user,
            content='Visa docs pending',
        )

        events = get_communication_history(
            company=self.company,
            student=self.student,
        )

        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]['type'], 'note')
