from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.constants import (
    ALL_PERMISSIONS,
    ROLE_ADMIN,
    ROLE_COUNSELLOR,
    ROLE_MANAGER,
    ROLE_PERMISSIONS,
    ROLE_TELECALLER,
)
from accounts.models import Company, CustomUser, Permission, Role, RolePermission
from auditlogs.models import AuditLog
from leads.models import Lead


class RBACHardeningTests(APITestCase):
    def setUp(self):
        self.company = Company.objects.create(name='RBAC Co')
        self.other_company = Company.objects.create(name='Other Co')

        self.admin_role = Role.objects.create(name=ROLE_ADMIN)
        self.manager_role = Role.objects.create(name=ROLE_MANAGER)
        self.counsellor_role = Role.objects.create(name=ROLE_COUNSELLOR)
        self.telecaller_role = Role.objects.create(name=ROLE_TELECALLER)

        perm_map = {
            code: Permission.objects.create(code=code, name=name)
            for code, name in ALL_PERMISSIONS
        }

        for role_name, codes in ROLE_PERMISSIONS.items():
            key = role_name.lower().replace(' ', '_') + '_role'
            role = getattr(self, key, None)
            if not role:
                continue
            for code in codes:
                RolePermission.objects.create(
                    role=role,
                    permission=perm_map[code],
                )

        self.admin = self._user('admin', self.admin_role)
        self.manager = self._user('manager', self.manager_role)
        self.counsellor = self._user('couns', self.counsellor_role)
        self.telecaller = self._user('tele', self.telecaller_role)

        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Test',
            last_name='Lead',
            phone='9000000001',
            status='interested',
            assigned_counsellor=self.counsellor,
        )

        AuditLog.objects.create(
            company=self.company,
            user=self.admin,
            module='Leads',
            action='create',
            object_id=self.lead.id,
            description='Test audit entry',
        )

    def _user(self, username, role):
        return CustomUser.objects.create_user(
            username=username,
            password='pass1234',
            company=self.company,
            role=role,
        )

    def _auth(self, user):
        token = RefreshToken.for_user(user)
        self.client.credentials(
            HTTP_AUTHORIZATION=f'Bearer {token.access_token}',
        )

    def test_telecaller_cannot_access_audit_logs(self):
        self._auth(self.telecaller)
        response = self.client.get('/api/auditlogs/')
        self.assertEqual(response.status_code, 403)

    def test_manager_can_access_audit_logs(self):
        self._auth(self.manager)
        response = self.client.get('/api/auditlogs/')
        self.assertEqual(response.status_code, 200)

    def test_cannot_convert_new_lead(self):
        self.lead.status = 'new'
        self.lead.save()
        self._auth(self.admin)
        response = self.client.post(
            f'/api/leads/{self.lead.id}/convert/',
        )
        self.assertEqual(response.status_code, 400)

    def test_counsellor_can_convert_interested_lead(self):
        self._auth(self.counsellor)
        response = self.client.post(
            f'/api/leads/{self.lead.id}/convert/',
        )
        self.assertEqual(response.status_code, 201)

    def test_tenant_isolation_leads_list(self):
        Lead.objects.create(
            company=self.other_company,
            first_name='Other',
            last_name='Lead',
            phone='9000000002',
        )
        self._auth(self.admin)
        response = self.client.get('/api/leads/')
        phones = [
            row['phone']
            for row in response.data['results']
        ]
        self.assertEqual(phones, ['9000000001'])
