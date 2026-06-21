from unittest.mock import MagicMock, patch

from django.test import TestCase

from accounts.models import Company, CustomUser

from admissions.models import Student

from leads.models import Lead

from whatsapp.message_service import connect_user_session
from whatsapp.models import WhatsAppAccount, WhatsAppMessage, WhatsAppServer
from whatsapp.openwa_client import (
    OpenWAClient,
    OpenWAError,
    extract_qr_payload,
    extract_session_id,
    fetch_session_qr,
    is_qr_not_ready_error,
    is_session_already_started_error,
    is_session_connected,
    is_session_missing_error,
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
        self.assertEqual(
            normalize_chat_id('9876543210', '917736425600'),
            '919876543210@c.us',
        )

    def test_humanize_openwa_error_lid(self):
        from whatsapp.openwa_client import humanize_openwa_error

        message = humanize_openwa_error(
            OpenWAError('HTTP 500: Error: No LID for user'),
        )
        self.assertIn('international', message.lower())

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
            {
                'qrCode': 'data:image/png;base64,abc',
                'status': 'qr_ready',
            },
        )
        self.assertEqual(qr['image'], 'data:image/png;base64,abc')
        self.assertEqual(qr['qr'], 'data:image/png;base64,abc')
        self.assertEqual(qr['status'], 'qr_ready')

    def test_is_session_connected(self):
        self.assertTrue(
            is_session_connected({'status': 'CONNECTED'}),
        )
        self.assertFalse(
            is_session_connected({'status': 'SCAN_QR'}),
        )

    def test_is_session_missing_error(self):
        self.assertTrue(
            is_session_missing_error(
                OpenWAError('HTTP 404: Session not found'),
            ),
        )
        self.assertFalse(
            is_session_missing_error(
                OpenWAError('HTTP 500: server error'),
            ),
        )

    def test_is_qr_not_ready_error(self):
        self.assertTrue(
            is_qr_not_ready_error(
                OpenWAError(
                    'HTTP 400: Session is not started. '
                    'Call POST /sessions/:id/start first.',
                ),
            ),
        )
        self.assertTrue(
            is_session_already_started_error(
                OpenWAError('HTTP 400: Session is already started'),
            ),
        )

    @patch('whatsapp.openwa_client.time.sleep')
    @patch.object(OpenWAClient, '_request')
    def test_fetch_session_qr_starts_then_polls(
        self,
        mock_request,
        _mock_sleep,
    ):
        mock_request.side_effect = [
            {'status': 'created'},  # get_session before start
            {},  # start
            OpenWAError('HTTP 400: QR code is not ready yet. Please wait...'),
            {
                'qrCode': 'data:image/png;base64,abc',
                'status': 'qr_ready',
            },
        ]

        client = OpenWAClient('http://localhost:2785/api', 'key')
        qr = fetch_session_qr(client, 'sess_1')

        self.assertEqual(qr['image'], 'data:image/png;base64,abc')
        self.assertEqual(mock_request.call_count, 4)
        self.assertEqual(
            mock_request.call_args_list[1][0],
            ('POST', '/sessions/sess_1/start'),
        )

    @patch.object(OpenWAClient, '_request')
    def test_safe_start_ignores_missing_route(self, mock_request):
        from whatsapp.openwa_client import OpenWAError

        mock_request.side_effect = [
            {'status': 'created'},
            OpenWAError('HTTP 404: Cannot POST /start'),
        ]
        client = OpenWAClient('http://localhost:2785/api', 'key')
        result = client.safe_start_session('sess_1')
        self.assertEqual(result, {})

    @patch.object(OpenWAClient, '_request')
    def test_send_text_uses_longer_timeout(self, mock_request):
        mock_request.return_value = {'messageId': 'msg-1'}
        client = OpenWAClient('http://localhost:2785/api', 'key')
        client.send_text('sess-1', '918281350086@c.us', 'hello')

        mock_request.assert_called_once()
        self.assertEqual(
            mock_request.call_args.kwargs.get('timeout'),
            180,
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
            session_id='pending-99',
            is_connected=False,
        )

    @patch('whatsapp.message_service.get_client_for_company')
    def test_send_whatsapp_message_success(self, mock_client_factory):
        self.account.session_id = 'sess-1'
        self.account.is_connected = False
        self.account.save()

        mock_client = MagicMock()
        mock_client.get_session.return_value = {'status': 'ready'}
        mock_client.send_text.return_value = {'messageId': 'msg-1'}
        mock_client_factory.return_value = (mock_client, MagicMock())

        record = send_whatsapp_message(
            company=self.company,
            user=self.user,
            recipient_number='9876543210',
            message='Hello',
            lead=self.lead,
        )

        self.assertEqual(record.status, 'sent')
        mock_client.get_session.assert_called()
        mock_client.start_session.assert_not_called()
        mock_client.send_text.assert_called_once()

        self.account.refresh_from_db()
        self.assertTrue(self.account.is_connected)

    @patch('whatsapp.message_service.get_client_for_company')
    def test_send_whatsapp_finds_user_account_before_connected_flag(
        self,
        mock_client_factory,
    ):
        self.account.session_id = 'sess-1'
        self.account.is_connected = False
        self.account.save()

        mock_client = MagicMock()
        mock_client.get_session.return_value = {'status': 'ready'}
        mock_client.send_text.return_value = {'messageId': 'msg-1'}
        mock_client_factory.return_value = (mock_client, MagicMock())

        record = send_whatsapp_message(
            company=self.company,
            user=self.user,
            recipient_number='9876543210',
            message='Hello',
        )

        self.assertEqual(record.status, 'sent')

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
        mock_client.get_session.return_value = {
            'status': 'qr_ready',
        }
        mock_client_factory.return_value = (mock_client, MagicMock())

        account, qr = connect_user_session(self.user)

        self.assertEqual(account.session_id, 'sess_new')
        self.assertTrue(qr.get('image'))

    @patch('whatsapp.message_service.get_client_for_company')
    def test_connect_recovers_deleted_openwa_session(
        self,
        mock_client_factory,
    ):
        self.account.session_id = 'deleted-openwa-session'
        self.account.save()

        mock_client = MagicMock()
        mock_client.health_ready.return_value = {'status': 'ok'}
        mock_client.get_session.side_effect = [
            OpenWAError('HTTP 404: Session not found'),
            {'status': 'qr_ready'},
            {'status': 'qr_ready'},
            {'status': 'qr_ready'},
        ]
        mock_client.find_session_by_name.return_value = None
        mock_client.ensure_session.return_value = {
            'id': 'sess_fresh',
            'status': 'qr_ready',
        }
        mock_client.get_qr.return_value = {
            'qrCode': 'data:image/png;base64,abc',
        }
        mock_client_factory.return_value = (mock_client, MagicMock())

        account, qr = connect_user_session(self.user)

        self.assertEqual(account.session_id, 'sess_fresh')
        mock_client.ensure_session.assert_called_once()
        self.assertTrue(qr.get('qr'))

    def test_follow_up_template(self):
        message = build_follow_up_message(
            self.lead,
            'WA Co',
        )

        self.assertIn('Whats', message)
        self.assertIn('WA Co', message)
