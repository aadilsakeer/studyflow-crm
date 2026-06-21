from django.utils import timezone

from rest_framework.exceptions import ValidationError
from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from admissions.models import Student
from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)
from auditlogs.helpers import log_audit
from core.mixins import CompanyFilteredMixin, require_company
from licensing.mixins import LicensedModuleMixin
from leads.models import Lead

from .history_service import (
    get_communication_history,
    get_company_communication_history,
)
from .models import CommunicationNote, EmailLog, WhatsAppLog
from .serializers import (
    CommunicationNoteSerializer,
    EmailLogSerializer,
    WhatsAppLogSerializer,
)


class EntityFilterMixin:

    def filter_by_entity(self, queryset):
        lead_id = self.request.query_params.get('lead')
        student_id = self.request.query_params.get(
            'student',
        )

        if lead_id:
            queryset = queryset.filter(lead_id=lead_id)

        if student_id:
            queryset = queryset.filter(
                student_id=student_id,
            )

        return queryset


class CommunicationNoteListCreateAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    CompanyFilteredMixin,
    EntityFilterMixin,
    ListCreateAPIView,
):
    licensed_module = 'crm'
    queryset = CommunicationNote.objects.all()
    serializer_class = CommunicationNoteSerializer
    permission_map = crm_permission_map('communications')

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'author',
            'lead',
            'student',
        )
        return self.filter_by_entity(
            queryset,
        ).order_by('-created_at')

    def perform_create(self, serializer):
        note = serializer.save(
            company=require_company(self.request.user),
            author=self.request.user,
        )
        log_audit(
            company=note.company,
            user=self.request.user,
            module='Communications',
            action='create',
            object_id=note.id,
            description='Communication note created.',
        )


class EmailLogListCreateAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    CompanyFilteredMixin,
    EntityFilterMixin,
    ListCreateAPIView,
):
    licensed_module = 'crm'
    queryset = EmailLog.objects.all()
    serializer_class = EmailLogSerializer
    permission_map = crm_permission_map('communications')

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'logged_by',
            'lead',
            'student',
        )
        return self.filter_by_entity(
            queryset,
        ).order_by('-sent_at')

    def perform_create(self, serializer):
        sent_at = serializer.validated_data.get(
            'sent_at',
        )

        if not sent_at:
            sent_at = timezone.now()

        email = serializer.save(
            company=require_company(self.request.user),
            logged_by=self.request.user,
            sent_at=sent_at,
        )
        log_audit(
            company=email.company,
            user=self.request.user,
            module='Communications',
            action='create',
            object_id=email.id,
            description='Email log created.',
        )


class WhatsAppLogListCreateAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    CompanyFilteredMixin,
    EntityFilterMixin,
    ListCreateAPIView,
):
    licensed_module = 'crm'
    queryset = WhatsAppLog.objects.all()
    serializer_class = WhatsAppLogSerializer
    permission_map = crm_permission_map('communications')

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            'logged_by',
            'lead',
            'student',
        )
        return self.filter_by_entity(
            queryset,
        ).order_by('-created_at')

    def perform_create(self, serializer):
        entry = serializer.save(
            company=require_company(self.request.user),
            logged_by=self.request.user,
        )
        log_audit(
            company=entry.company,
            user=self.request.user,
            module='Communications',
            action='create',
            object_id=entry.id,
            description='WhatsApp log created.',
        )


class CommunicationHistoryAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    APIView,
):
    licensed_module = 'crm'
    permission_map = crm_permission_map('communications')

    def get(self, request):
        company = require_company(request.user)

        lead_id = request.query_params.get('lead')
        student_id = request.query_params.get('student')
        comm_type = request.query_params.get('type')
        limit = request.query_params.get('limit', 100)

        try:
            limit = int(limit)
        except (TypeError, ValueError):
            limit = 100

        limit = max(1, min(limit, 100))

        lead = None
        student = None

        if lead_id:
            lead = Lead.objects.filter(
                pk=lead_id,
                company=company,
                is_deleted=False,
            ).first()

            if not lead:
                raise ValidationError(
                    {'lead': 'Lead not found.'},
                )

        if student_id:
            student = Student.objects.filter(
                pk=student_id,
                company=company,
                is_deleted=False,
            ).select_related('lead').first()

            if not student:
                raise ValidationError(
                    {'student': 'Student not found.'},
                )

        if lead or student:
            events = get_communication_history(
                company=company,
                lead=lead,
                student=student,
                limit=limit,
            )
        else:
            events = get_company_communication_history(
                company=company,
                comm_type=comm_type,
                limit=limit,
            )

        return Response({'events': events})
