from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import CustomUser
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)
from accounts.constants import PERM_LEADS_ASSIGN

from .api_views import LeadQuerysetMixin
from .assignment_service import (
    assign_leads_to_telecaller,
    get_assignable_leads,
    get_company_telecallers,
    round_robin_assign_leads,
    validate_telecaller,
)
from .serializers import LeadSerializer


class TelecallerListAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN),
    ]

    def get(self, request):
        company = self.get_company()

        if not company:
            return Response([])

        telecallers = get_company_telecallers(company)

        data = [
            {
                'id': user.id,
                'username': user.username,
                'display_name': (
                    user.get_full_name()
                    or user.username
                ),
            }
            for user in telecallers
        ]

        return Response(data)


class LeadAssignAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN),
    ]

    def post(self, request, pk):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {'detail': 'Company not found.'},
            )

        telecaller_id = request.data.get('telecaller_id')

        if not telecaller_id:
            raise ValidationError(
                {'telecaller_id': 'This field is required.'},
            )

        telecaller = get_object_or_404(
            CustomUser.objects.filter(company=company),
            pk=telecaller_id,
        )
        validate_telecaller(telecaller, company)

        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )

        assign_leads_to_telecaller(
            [lead],
            telecaller,
            request.user,
        )

        return Response(
            LeadSerializer(
                lead,
                context={'request': request},
            ).data,
        )


class LeadBulkAssignAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN),
    ]

    def post(self, request):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {'detail': 'Company not found.'},
            )

        lead_ids = request.data.get('lead_ids', [])
        telecaller_id = request.data.get('telecaller_id')

        if not lead_ids:
            raise ValidationError(
                {'lead_ids': 'Select at least one lead.'},
            )

        if not telecaller_id:
            raise ValidationError(
                {'telecaller_id': 'This field is required.'},
            )

        telecaller = get_object_or_404(
            CustomUser.objects.filter(company=company),
            pk=telecaller_id,
        )
        validate_telecaller(telecaller, company)

        leads = get_assignable_leads(
            self.get_lead_queryset(),
            lead_ids,
        )

        assign_leads_to_telecaller(
            leads,
            telecaller,
            request.user,
        )

        return Response(
            {
                'assigned_count': len(leads),
                'telecaller_id': telecaller.id,
            },
            status=status.HTTP_200_OK,
        )


class LeadRoundRobinAssignAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_ASSIGN),
    ]

    def post(self, request):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {'detail': 'Company not found.'},
            )

        lead_ids = request.data.get('lead_ids', [])

        if not lead_ids:
            raise ValidationError(
                {'lead_ids': 'Select at least one lead.'},
            )

        leads = get_assignable_leads(
            self.get_lead_queryset(),
            lead_ids,
        )

        round_robin_assign_leads(
            leads,
            company,
            request.user,
        )

        return Response(
            {'assigned_count': len(leads)},
            status=status.HTTP_200_OK,
        )
