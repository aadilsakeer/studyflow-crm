from rest_framework.exceptions import NotFound
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.access import filter_students_for_user
from accounts.constants import PERM_LEADS_VIEW, PERM_STUDENTS_VIEW
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from admissions.models import Student

from leads.api_views import LeadQuerysetMixin

from .timeline_service import (
    get_lead_timeline,
    get_student_timeline,
    timeline_response,
)


class LeadActivityTimelineAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_VIEW),
    ]

    def get(self, request, pk):
        lead = self.get_lead_queryset().filter(pk=pk).first()

        if not lead:
            raise NotFound('Lead not found.')

        event_type = request.query_params.get('event_type')
        limit = request.query_params.get('limit')
        events = get_lead_timeline(lead, event_type)

        if limit:
            try:
                limit_value = max(1, min(int(limit), 100))
            except (TypeError, ValueError):
                limit_value = 20
            events = events[:limit_value]

        return Response(
            timeline_response(
                'lead',
                lead.id,
                f'{lead.first_name} {lead.last_name}'.strip(),
                events,
            ),
        )


class StudentActivityTimelineAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_STUDENTS_VIEW),
    ]

    def get_company(self):
        return getattr(self.request.user, 'company', None)

    def get(self, request, pk):
        company = self.get_company()

        if not company:
            raise NotFound('Student not found.')

        student = filter_students_for_user(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            request.user,
        ).filter(pk=pk).first()

        if not student:
            raise NotFound('Student not found.')

        event_type = request.query_params.get('event_type')
        events = get_student_timeline(student, event_type)

        return Response(
            timeline_response(
                'student',
                student.id,
                student.student_id,
                events,
            ),
        )
