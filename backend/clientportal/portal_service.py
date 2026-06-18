import os

from rest_framework.exceptions import AuthenticationFailed, ValidationError
from rest_framework.permissions import BasePermission

from activity.timeline_constants import EVENT_DOCUMENT_UPLOADED
from activity.timeline_service import record_student_event

from admissions.models import (
    Application,
    OfferLetter,
    StudentDocument,
    VisaCase,
)

from .portal_auth import PortalTokenService


class PortalAuthenticatedMixin:

    portal_header = 'HTTP_X_PORTAL_TOKEN'

    def get_portal_access(self):
        token = self.request.META.get(self.portal_header)

        if not token:
            auth = self.request.headers.get('Authorization', '')

            if auth.startswith('Portal '):
                token = auth.split(' ', 1)[1]

        portal = PortalTokenService.resolve_portal(token)

        if not portal:
            raise AuthenticationFailed('Invalid or expired portal session.')

        return portal

    def get_student(self):
        return self.get_portal_access().student


class IsPortalAuthenticated(BasePermission):

    def has_permission(self, request, view):
        try:
            view.get_portal_access()
        except AuthenticationFailed:
            return False

        return True


ALLOWED_EXTENSIONS = {
    '.pdf',
    '.jpg',
    '.jpeg',
    '.png',
    '.doc',
    '.docx',
}
MAX_FILE_SIZE = 10 * 1024 * 1024


def validate_upload_file(uploaded_file):
    if not uploaded_file:
        raise ValidationError({'file': 'File is required.'})

    ext = os.path.splitext(
        uploaded_file.name,
    )[1].lower()

    if ext not in ALLOWED_EXTENSIONS:
        raise ValidationError({'file': 'Unsupported file type.'})

    if uploaded_file.size > MAX_FILE_SIZE:
        raise ValidationError({'file': 'File exceeds 10MB limit.'})


def serialize_document(document):
    return {
        'id': document.id,
        'document_type': document.document_type,
        'document_type_display': (
            document.get_document_type_display()
        ),
        'status': document.status,
        'status_display': document.get_status_display(),
        'notes': document.notes,
        'rejection_remarks': document.rejection_remarks,
        'has_file': bool(document.file),
        'original_filename': document.original_filename,
        'updated_at': document.updated_at,
    }


def serialize_application(application):
    return {
        'id': application.id,
        'university_name': application.university_name,
        'course_name': application.course_name,
        'intake': application.intake,
        'status': application.application_status,
        'created_at': application.created_at,
    }


def serialize_offer(offer):
    return {
        'id': offer.id,
        'university': offer.university,
        'course': offer.course,
        'offer_number': offer.offer_number,
        'status': offer.status,
        'status_display': offer.get_status_display(),
        'issue_date': offer.issue_date,
        'expiry_date': offer.expiry_date,
    }


def serialize_visa(case):
    return {
        'id': case.id,
        'country': case.country,
        'visa_type': case.visa_type,
        'status': case.status,
        'status_display': case.get_status_display(),
        'appointment_date': case.appointment_date,
        'submission_date': case.submission_date,
        'decision_date': case.decision_date,
    }


def upload_student_document(portal, document_id, uploaded_file):
    student = portal.student

    document = StudentDocument.objects.filter(
        pk=document_id,
        student=student,
        company=student.company,
        is_deleted=False,
    ).first()

    if not document:
        raise ValidationError({'detail': 'Document not found.'})

    if document.status not in ('requested', 'rejected'):
        raise ValidationError(
            {'detail': 'Document cannot be uploaded in current status.'},
        )

    validate_upload_file(uploaded_file)

    document.file = uploaded_file
    document.original_filename = uploaded_file.name
    document.file_size = uploaded_file.size
    document.mime_type = getattr(
        uploaded_file,
        'content_type',
        '',
    ) or ''
    document.status = 'uploaded'
    document.rejection_remarks = ''
    document.save()

    record_student_event(
        student,
        EVENT_DOCUMENT_UPLOADED,
        description=(
            f'{document.get_document_type_display()} '
            f'uploaded via student portal.'
        ),
        user=None,
    )

    return document
