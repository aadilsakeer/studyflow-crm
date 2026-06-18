from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from activity.timeline_service import get_student_timeline

from admissions.models import Application, OfferLetter, StudentDocument, VisaCase

from .portal_auth import authenticate_portal, PortalTokenService
from .portal_service import (
    PortalAuthenticatedMixin,
    serialize_application,
    serialize_document,
    serialize_offer,
    serialize_visa,
    upload_student_document,
)


class PortalLoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        if not username or not password:
            raise ValidationError(
                {'detail': 'Username and password required.'},
            )

        portal = authenticate_portal(username, password)

        if not portal:
            raise ValidationError(
                {'detail': 'Invalid portal credentials.'},
            )

        student = portal.student
        token = PortalTokenService.create_token(portal)

        return Response({
            'token': token,
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'destination_country': student.destination_country,
                'status': student.status,
            },
        })


class PortalProfileAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        portal = self.get_portal_access()
        student = portal.student

        return Response({
            'username': portal.username,
            'student': {
                'id': student.id,
                'student_id': student.student_id,
                'destination_country': student.destination_country,
                'preferred_university': student.preferred_university,
                'status': student.status,
            },
        })


class PortalDocumentsAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        student = self.get_student()

        documents = StudentDocument.objects.filter(
            student=student,
            company=student.company,
            is_deleted=False,
        ).order_by('-updated_at')

        return Response([
            serialize_document(document)
            for document in documents
        ])


class PortalDocumentUploadAPIView(
    PortalAuthenticatedMixin,
    APIView,
):
    authentication_classes = []
    permission_classes = []
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        portal = self.get_portal_access()
        uploaded = request.FILES.get('file')

        document = upload_student_document(
            portal,
            pk,
            uploaded,
        )

        return Response(serialize_document(document))


class PortalApplicationsAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        student = self.get_student()

        applications = Application.objects.filter(
            student=student,
            is_deleted=False,
        ).order_by('-created_at')

        return Response([
            serialize_application(item)
            for item in applications
        ])


class PortalOffersAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        student = self.get_student()

        offers = OfferLetter.objects.filter(
            student=student,
            company=student.company,
            is_deleted=False,
        ).order_by('-created_at')

        return Response([
            serialize_offer(item)
            for item in offers
        ])


class PortalVisaCasesAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        student = self.get_student()

        cases = VisaCase.objects.filter(
            student=student,
            company=student.company,
            is_deleted=False,
        ).order_by('-created_at')

        return Response([
            serialize_visa(item)
            for item in cases
        ])


class PortalTimelineAPIView(PortalAuthenticatedMixin, APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request):
        student = self.get_student()
        events = get_student_timeline(student)

        return Response({
            'student_id': student.student_id,
            'events': events,
        })
