from unittest.mock import MagicMock, patch

from django.test import TestCase

from accounts.models import Company, CustomUser

from admissions.models import Student

from leads.models import Lead

from whatsapp.message_service import send_whatsapp_message
from whatsapp.models import WhatsAppAccount, WhatsAppMessage, WhatsAppServer
from whatsapp.openwa_client import normalize_chat_id
from whatsapp.templates import build_follow_up_message


class OpenWAClientTests(TestCase):

    def test_normalize_chat_id(self):
        self.assertEqual(
            normalize_chat_id('+91 9876543210'),
            '919876543210@c.us',
        )


class WhatsAppSendTests(TestCase):

    def setUp(self):
        self.company = Company.objects.create(name='WA Co')
        self.user = CustomUser.objects.create_user(
            username='wauser',
            password='pass12345',
            company=self.company,
        )
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Whats',
            last_name='App',
            phone='9876543210',
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-WA-1',
        )
        WhatsAppServer.objects.create(
            company=self.company,
            base_url='http://localhost:2785/api',
            api_key='test-key',
            is_active=True,
        )
        self.account = WhatsAppAccount.objects.create(
            company=self.company,
            user=self.user,
            phone_number='9999999999',
            session_id='session-1',
            is_connected=True,
        )

    @patch('whatsapp.message_service.get_client_for_company')
    def test_send_whatsapp_message_success(self, mock_client_factory):
        mock_client = MagicMock()
        mock_client.send_text.return_value = {'ok': True}
        mock_client_factory.return_value = (mock_client, MagicMock())

        record = send_whatsapp_message(
            company=self.company,
            user=self.user,
            recipient_number='9876543210',
            message='Hello',
            lead=self.lead,
        )

        self.assertEqual(record.status, 'sent')
        self.assertEqual(
            WhatsAppMessage.objects.count(),
            1,
        )
        mock_client.send_text.assert_called_once()

    def test_follow_up_template(self):
        message = build_follow_up_message(
            self.lead,
            'WA Co',
        )

        self.assertIn('Whats', message)
        self.assertIn('WA Co', message)
