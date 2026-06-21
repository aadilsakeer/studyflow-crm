from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_LEADS_CHANGE, PERM_LEADS_VIEW
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from admissions.models import Student
from auditlogs.services import AuditLogService

from .api_views import LeadQuerysetMixin
from .journey_board import get_journey_board, move_to_stage
from .models import Lead


class JourneyBoardAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_VIEW),
    ]

    def get(self, request):
        company = self.get_company()

        if not company:
            return Response({'stages': [], 'total': 0})

        filters = {
            k: request.query_params.get(k)
            for k in (
                'search',
                'telecaller',
                'counsellor',
                'country',
                'university',
            )
            if request.query_params.get(k)
        }

        return Response(
            get_journey_board(
                company,
                request.user,
                filters,
            ),
        )


class JourneyBoardMoveAPIView(LeadQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_CHANGE),
    ]

    def patch(self, request, entity_type, pk):
        company = self.get_company()
        stage = request.data.get('stage')

        if not stage:
            raise ValidationError({'stage': 'Required.'})

        try:
            card = move_to_stage(
                entity_type,
                pk,
                stage,
                company,
                request.user,
            )
        except Lead.DoesNotExist:
            raise ValidationError({'detail': 'Lead not found.'}) from None
        except Student.DoesNotExist:
            raise ValidationError({'detail': 'Student not found.'}) from None
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)}) from exc

        AuditLogService.log(
            company=company,
            user=request.user,
            module='Journey Board',
            action='move',
            object_id=pk,
            description=(
                f'Moved {entity_type} {pk} to {stage}'
            ),
        )

        return Response(card)
