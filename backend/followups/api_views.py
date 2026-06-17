from django.utils import timezone

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from core.mixins import LeadCompanyFilteredMixin

from leads.models import FollowUp
from .serializers import FollowUpSerializer


class FollowUpListAPIView(
    LeadCompanyFilteredMixin,
    ListCreateAPIView,
):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer

    def get_queryset(self):
        queryset = super().get_queryset()

        lead_id = self.request.query_params.get(
            "lead",
        )
        completed = self.request.query_params.get(
            "completed",
        )
        date_filter = self.request.query_params.get(
            "date",
        )

        if lead_id:
            queryset = queryset.filter(
                lead_id=lead_id,
            )

        if completed is not None:
            queryset = queryset.filter(
                completed=(
                    completed.lower() == "true"
                ),
            )

        today = timezone.localdate()

        if date_filter == "today":
            queryset = queryset.filter(
                follow_up_date__date=today,
            )

        if date_filter == "completed_today":
            queryset = queryset.filter(
                completed=True,
                completed_at__date=today,
            )

        return queryset.order_by(
            "-follow_up_date",
        )

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
                "You cannot add follow-ups "
                "to this lead."
            )

        serializer.save()


class FollowUpDetailAPIView(
    LeadCompanyFilteredMixin,
    RetrieveUpdateDestroyAPIView,
):
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
