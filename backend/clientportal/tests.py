from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import Company

from admissions.models import Application, Student, StudentDocument
from clientportal.models import ClientPortalAccess
from clientportal.portal_auth import (
    PortalTokenService,
    authenticate_portal,
)
from clientportal.portal_service import upload_student_document
from clientportal.services import ClientPortalAuthService

from leads.models import Lead


class PortalAuthTests(TestCase):
    def setUp(self):
        self.company = Company.objects.create(name='Portal Co')
        self.lead = Lead.objects.create(
            company=self.company,
            first_name='Portal',
            last_name='Student',
            phone='9333333333',
        )
        self.student = Student.objects.create(
            company=self.company,
            lead=self.lead,
            student_id='STU-PORT-1',
        )
        self.portal = ClientPortalAccess.objects.create(
            student=self.student,
            username='portaluser',
            password=ClientPortalAuthService.hash_password('secret123'),
        )

    def test_login_and_token(self):
        portal = authenticate_portal('portaluser', 'secret123')

        self.assertIsNotNone(portal)

        token = PortalTokenService.create_token(portal)
        resolved = PortalTokenService.resolve_portal(token)

        self.assertEqual(resolved.id, self.portal.id)

    def test_document_upload(self):
        document = StudentDocument.objects.create(
            company=self.company,
            student=self.student,
            document_type='passport',
            status='requested',
        )

        upload = SimpleUploadedFile(
            'passport.pdf',
            b'pdf-content',
            content_type='application/pdf',
        )

        updated = upload_student_document(
            self.portal,
            document.id,
            upload,
        )

        self.assertEqual(updated.status, 'uploaded')
        self.assertTrue(updated.file)

    def test_applications_scoped_to_student(self):
        Application.objects.create(
            student=self.student,
            university_name='Uni A',
            course_name='CS',
            intake='Fall 2026',
        )

        self.assertEqual(
            Application.objects.filter(
                student=self.student,
            ).count(),
            1,
        )
