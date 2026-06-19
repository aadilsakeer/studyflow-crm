import pyotp
from django.test import TestCase
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import Company, CustomUser
from security.models import LoginAttempt, SecurityEvent, UserSecurityProfile
from security.services import (
    enable_totp,
    record_login_attempt,
    security_dashboard,
    setup_totp,
    validate_password_policy,
    verify_2fa,
)


class SecurityServiceTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Sec Co')
        self.user = CustomUser.objects.create_user(
            username='secuser',
            email='sec@co.com',
            password='OldPass1',
            company=self.company,
        )

    def test_password_policy_rejects_weak(self):
        with self.assertRaises(Exception):
            validate_password_policy('weak', user=self.user)

    def test_password_policy_accepts_strong(self):
        validate_password_policy('StrongPass1', user=self.user)

    def test_totp_setup_and_enable(self):
        setup = setup_totp(self.user)
        self.assertIn('secret', setup)
        profile = UserSecurityProfile.objects.get(user=self.user)
        code = pyotp.TOTP(profile.totp_secret).now()
        result = enable_totp(self.user, code)
        self.assertEqual(len(result['backup_codes']), 8)
        profile.refresh_from_db()
        self.assertTrue(profile.totp_enabled)

    def test_verify_2fa_with_backup_code(self):
        setup_totp(self.user)
        profile = UserSecurityProfile.objects.get(user=self.user)
        code = pyotp.TOTP(profile.totp_secret).now()
        result = enable_totp(self.user, code)
        backup = result['backup_codes'][0]
        verify_2fa(self.user, backup_code=backup)
        profile.refresh_from_db()
        self.assertEqual(len(profile.backup_codes), 7)

    def test_failed_login_tracking(self):
        for _ in range(5):
            record_login_attempt(
                username='secuser',
                user=None,
                success=False,
                ip='10.0.0.1',
                user_agent='TestAgent',
                reason='bad_password',
            )
        suspicious = LoginAttempt.objects.filter(is_suspicious=True).count()
        self.assertGreaterEqual(suspicious, 1)

    def test_dashboard_tenant_isolation(self):
        other = Company.objects.create(name='Other Co')
        CustomUser.objects.create_user(
            username='other',
            password='OtherPass1',
            company=other,
        )
        record_login_attempt(
            username='secuser', user=self.user, success=True,
            ip='1.1.1.1', user_agent='A',
        )
        record_login_attempt(
            username='other', user=None, success=False,
            ip='2.2.2.2', user_agent='B', reason='fail',
        )
        LoginAttempt.objects.filter(username_attempted='other').update(company=other)

        dash = security_dashboard(self.user)
        self.assertEqual(dash['successful_logins_24h'], 1)
        self.assertEqual(dash['failed_logins_24h'], 0)

        superuser = CustomUser.objects.create_superuser(
            username='super', email='s@t.com', password='SuperPass1',
        )
        super_dash = security_dashboard(superuser)
        self.assertGreaterEqual(super_dash['failed_logins_24h'], 1)


class SecurityAPITests(APITestCase):
    def setUp(self):
        self.company_a = Company.objects.create(name='Tenant A')
        self.company_b = Company.objects.create(name='Tenant B')
        self.user_a = CustomUser.objects.create_user(
            username='usera',
            email='a@t.com',
            password='PassWord1',
            company=self.company_a,
        )
        self.user_b = CustomUser.objects.create_user(
            username='userb',
            email='b@t.com',
            password='PassWord1',
            company=self.company_b,
        )
        self.superuser = CustomUser.objects.create_superuser(
            username='super',
            email='super@t.com',
            password='SuperPass1',
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token.access_token}')

    def test_login_records_attempt(self):
        r = self.client.post('/api/token/', {
            'username': 'usera',
            'password': 'PassWord1',
        })
        self.assertEqual(r.status_code, 200)
        self.assertTrue(
            LoginAttempt.objects.filter(username_attempted='usera', success=True).exists()
        )
        self.assertTrue(
            SecurityEvent.objects.filter(user=self.user_a, event_type='login_success').exists()
        )

    def test_2fa_setup_and_login(self):
        self._auth(self.user_a)
        setup = self.client.post('/api/security/2fa/setup/')
        self.assertEqual(setup.status_code, 200)
        secret = setup.data['secret']
        code = pyotp.TOTP(secret).now()
        enable = self.client.post('/api/security/2fa/enable/', {'code': code})
        self.assertEqual(enable.status_code, 200)
        self.assertEqual(len(enable.data['backup_codes']), 8)

        self.client.credentials()
        bad = self.client.post('/api/token/', {
            'username': 'usera',
            'password': 'PassWord1',
        })
        self.assertEqual(bad.status_code, 400)

        good = self.client.post('/api/token/', {
            'username': 'usera',
            'password': 'PassWord1',
            'totp_code': pyotp.TOTP(secret).now(),
        })
        self.assertEqual(good.status_code, 200)

    def test_password_policy_api(self):
        self._auth(self.user_a)
        weak = self.client.post('/api/security/password/check/', {'password': 'weak'})
        self.assertFalse(weak.data['valid'])
        strong = self.client.post('/api/security/password/check/', {'password': 'StrongPass1'})
        self.assertTrue(strong.data['valid'])

    def test_dashboard_tenant_scoped(self):
        record_login_attempt(
            username='usera', user=self.user_a, success=True,
            ip='1.1.1.1', user_agent='UA',
        )
        record_login_attempt(
            username='userb', user=None, success=False,
            ip='2.2.2.2', user_agent='UA', reason='bad',
        )
        LoginAttempt.objects.filter(username_attempted='userb').update(company=self.company_b)

        self._auth(self.user_a)
        r = self.client.get('/api/security/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['successful_logins_24h'], 1)
        self.assertEqual(r.data['failed_logins_24h'], 0)

    def test_superuser_sees_all_tenants(self):
        self._auth(self.superuser)
        r = self.client.get('/api/security/dashboard/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('recent_attempts', r.data)

    def test_revoke_sessions(self):
        self._auth(self.user_a)
        r = self.client.post('/api/security/sessions/revoke/', {})
        self.assertEqual(r.status_code, 200)
        self.assertIn('revoked', r.data)

    def test_user_security_events(self):
        SecurityEvent.objects.create(
            user=self.user_a,
            company=self.company_a,
            event_type='login_success',
            ip_address='1.1.1.1',
        )
        self._auth(self.user_a)
        r = self.client.get('/api/security/events/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(len(r.data['events']), 1)

    def test_tenant_cannot_view_other_events(self):
        SecurityEvent.objects.create(
            user=self.user_b,
            company=self.company_b,
            event_type='login_success',
        )
        self._auth(self.user_a)
        r = self.client.get(f'/api/security/events/?user_id={self.user_b.id}')
        self.assertEqual(r.status_code, 403)
