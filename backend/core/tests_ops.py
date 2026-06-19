from django.test import TestCase, override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from core.operations import (
    check_email_config,
    operations_snapshot,
    verify_latest_backup,
)


class OpsServiceTests(TestCase):
    def test_email_config(self):
        r = check_email_config()
        self.assertIn('backend', r)

    def test_operations_snapshot(self):
        snap = operations_snapshot()
        self.assertIn('status', snap)
        self.assertIn('alerts', snap)

    def test_verify_backup_empty(self):
        with override_settings(BACKUP_DIR='/tmp/nonexistent_backup_dir_xyz'):
            r = verify_latest_backup()
            self.assertFalse(r['ok'])


class OpsAPITests(APITestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_superuser(
            username='ops', email='ops@t.com', password='pass1234',
        )
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {RefreshToken.for_user(self.admin).access_token}',
        )

    def test_operations_dashboard(self):
        r = self.client.get('/api/health/operations/')
        self.assertEqual(r.status_code, 200)
        self.assertIn('celery', r.data)

    def test_health_public(self):
        self.client.credentials()
        r = self.client.get('/api/health/')
        self.assertEqual(r.status_code, 200)
