from unittest.mock import MagicMock, patch

from django.test import TestCase

from accounts.models import Company, CustomUser

from admissions.models import Student

from leads.models import Lead

from whatsapp.message_service import connect_user_session
from whatsapp.models import WhatsAppAccount, WhatsAppMessage, WhatsAppServer
from whatsapp.openwa_client import (
    OpenWAClient,
    extract_qr_payload,
    extract_session_id,
    is_session_connected,
    normalize_chat_id,
    normalize_base_url,
)
from whatsapp.message_service import send_whatsapp_message
from whatsapp.templates import build_follow_up_message


class OpenWAClientTests(TestCase):

    def test_normalize_chat_id(self):
        self.assertEqual(
            normalize_chat_id('+91 9876543210'),
            '919876543210@c.us',
        )

    def test_normalize_base_url(self):
        self.assertEqual(
            normalize_base_url('http://localhost:2785'),
            'http://localhost:2785/api',
        )
        self.assertEqual(
            normalize_base_url('http://localhost:2785/api'),
            'http://localhost:2785/api',
        )

    def test_extract_session_id(self):
        self.assertEqual(
            extract_session_id({'id': 'sess_abc'}),
            'sess_abc',
        )

    def test_extract_qr_payload(self):
        qr = extract_qr_payload(
            {'image': 'data:image/png;base64,abc', 'code': '123'},
        )
        self.assertEqual(qr['image'], 'data:image/png;base64,abc')

    def test_is_session_connected(self):
        self.assertTrue(
            is_session_connected({'status': 'CONNECTED'}),
        )
        self.assertFalse(
            is_session_connected({'status': 'SCAN_QR'}),
        )

    @patch.object(OpenWAClient, '_request')
    def test_safe_start_ignores_missing_route(self, mock_request):
        from whatsapp.openwa_client import OpenWAError

        mock_request.side_effect = OpenWAError('HTTP 404: Cannot POST /start')
        client = OpenWAClient('http://localhost:2785/api', 'key')
        result = client.safe_start_session('sess_1')
        self.assertEqual(result, {})


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
            session_id='pending-99',
            is_connected=False,
        )

    @patch('whatsapp.message_service.get_client_for_company')
    def test_send_whatsapp_message_success(self, mock_client_factory):
        self.account.session_id = 'sess-1'
        self.account.is_connected = True
        self.account.save()

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

    @patch('whatsapp.message_service.get_client_for_company')
    def test_connect_user_session(self, mock_client_factory):
        mock_client = MagicMock()
        mock_client.health_ready.return_value = {'status': 'ok'}
        mock_client.ensure_session.return_value = {
            'id': 'sess_new',
            'status': 'SCAN_QR',
        }
        mock_client.get_qr.return_value = {
            'image': 'data:image/png;base64,abc',
        }
        mock_client_factory.return_value = (mock_client, MagicMock())

        account, qr = connect_user_session(self.user)

        self.assertEqual(account.session_id, 'sess_new')
        self.assertTrue(qr.get('image'))

    def test_follow_up_template(self):
        message = build_follow_up_message(
            self.lead,
            'WA Co',
        )

        self.assertIn('Whats', message)
        self.assertIn('WA Co', message)
