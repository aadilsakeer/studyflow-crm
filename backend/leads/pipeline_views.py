from django.shortcuts import get_object_or_404

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import (
    PERM_LEADS_ASSIGN_COUNSELLOR,
    PERM_LEADS_CHANGE,
    PERM_LEADS_QUALIFY,
)
from accounts.models import CustomUser
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from .api_views import LeadQuerysetMixin
from .pipeline_service import (
    advance_pipeline,
    assign_counsellor,
    get_company_counsellors,
    qualify_lead,
    update_pipeline_data,
)
from .serializers import LeadSerializer


class CounsellorListAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN_COUNSELLOR),
    ]

    def get(self, request):
        company = self.get_company()

        if not company:
            return Response([])

        counsellors = get_company_counsellors(company)

        return Response([
            {
                'id': user.id,
                'username': user.username,
                'display_name': (
                    user.get_full_name() or user.username
                ),
            }
            for user in counsellors
        ])


class LeadQualifyAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_QUALIFY),
    ]

    def post(self, request, pk):
        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )
        qualify_lead(lead, request.user)

        return Response(
            LeadSerializer(
                lead,
                context={'request': request},
            ).data,
        )


class LeadAssignCounsellorAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN_COUNSELLOR),
    ]

    def post(self, request, pk):
        company = self.get_company()
        counsellor_id = request.data.get('counsellor_id')

        if not counsellor_id:
            raise ValidationError(
                {'counsellor_id': 'This field is required.'},
            )

        counsellor = get_object_or_404(
            CustomUser.objects.filter(company=company),
            pk=counsellor_id,
        )

        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )
        assign_counsellor(lead, counsellor, request.user)

        return Response(
            LeadSerializer(
                lead,
                context={'request': request},
            ).data,
        )


class LeadPipelineAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_CHANGE),
    ]

    def patch(self, request, pk):
        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )
        update_pipeline_data(lead, request.user, request.data)

        return Response(
            LeadSerializer(
                lead,
                context={'request': request},
            ).data,
        )


class LeadAdvancePipelineAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_CHANGE),
    ]

    def post(self, request, pk):
        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )
        advance_pipeline(lead, request.user)

        return Response(
            LeadSerializer(
                lead,
                context={'request': request},
            ).data,
        )
