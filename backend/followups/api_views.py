from django.utils import timezone

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)

from auditlogs.helpers import log_audit
from core.mixins import LeadCompanyFilteredMixin
from licensing.mixins import LicensedModuleMixin

from leads.models import FollowUp
from .serializers import FollowUpSerializer


class FollowUpListAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    ListCreateAPIView,
):
    licensed_module = 'crm'
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_map = crm_permission_map("followups")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            "lead",
            "assigned_to",
        )

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

        if (
            not lead.company_id
            or lead.company_id != company.id
        ):
            from rest_framework.exceptions import (
                PermissionDenied,
            )

            raise PermissionDenied(
                "You cannot add follow-ups "
                "to this lead."
            )

        follow_up = serializer.save()
        log_audit(
            company=company,
            user=self.request.user,
            module='FollowUps',
            action='create',
            object_id=follow_up.id,
            description=f"Follow-up created for lead {lead.id}.",
        )


class FollowUpDetailAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    RetrieveUpdateDestroyAPIView,
):
    licensed_module = 'crm'
    queryset = FollowUp.objects.all()
    serializer_class = FollowUpSerializer
    permission_map = crm_permission_map("followups")

    def perform_update(self, serializer):
        follow_up = serializer.save()
        company = getattr(self.request.user, 'company', None)
        log_audit(
            company=company,
            user=self.request.user,
            module='FollowUps',
            action='update',
            object_id=follow_up.id,
            description=f"Follow-up {follow_up.id} updated.",
        )

    def perform_destroy(self, instance):
        company = getattr(self.request.user, 'company', None)
        object_id = instance.id
        instance.delete()
        log_audit(
            company=company,
            user=self.request.user,
            module='FollowUps',
            action='delete',
            object_id=object_id,
            description=f"Follow-up {object_id} deleted.",
        )
