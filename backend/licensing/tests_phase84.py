from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase
import hmac
import hashlib

from licensing.razorpay_service import RazorpayBillingService
from licensing.models import SubscriptionPlan
from core.health import health_snapshot, check_env


class Phase84Tests(TestCase):
    @override_settings(RAZORPAY_WEBHOOK_SECRET='testsecret')
    def test_razorpay_signature_verification(self):
        body = b'{"event":"test"}'
        sig = hmac.new(b'testsecret', body, hashlib.sha256).hexdigest()
        self.assertTrue(RazorpayBillingService.verify_webhook_signature(body, sig))
        self.assertFalse(RazorpayBillingService.verify_webhook_signature(body, 'bad'))

    def test_health_snapshot(self):
        snap = health_snapshot()
        self.assertIn('status', snap)
        self.assertIn('database', snap)

    def test_env_check(self):
        self.assertTrue(check_env()['ok'])


class HealthAPITests(APITestCase):
    def test_health_endpoint(self):
        r = self.client.get('/api/health/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('status', r.data)

    def test_public_branding(self):
        r = self.client.get('/api/saas/branding/public/')
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data['brand_name'], 'Globvio')
