from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from core.mixins import LeadCompanyFilteredMixin

from leads.models import CallLog
from .serializers import CallLogSerializer


class CallLogListAPIView(
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    ListCreateAPIView,
):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    permission_map = crm_permission_map("calllogs")

    def get_queryset(self):
        queryset = super().get_queryset()

        lead_id = self.request.query_params.get(
            "lead",
        )

        if lead_id:
            queryset = queryset.filter(
                lead_id=lead_id,
            )

        return queryset.order_by("-call_time")

    def perform_create(self, serializer):
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            from rest_framework.exceptions import (
                ValidationError,
            )

            raise ValidationError(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                }
            )

        lead = serializer.validated_data.get(
            "lead",
        )

        if lead.company_id != company.id:
            from rest_framework.exceptions import (
                PermissionDenied,
            )

            raise PermissionDenied(
                "You cannot log calls "
                "for this lead."
            )

        serializer.save(
            called_by=self.request.user,
        )


class CallLogDetailAPIView(
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    RetrieveUpdateDestroyAPIView,
):
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    permission_map = crm_permission_map("calllogs")
