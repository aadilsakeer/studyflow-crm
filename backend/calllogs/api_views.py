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

from leads.models import CallLog
from .serializers import CallLogSerializer


class CallLogListAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    ListCreateAPIView,
):
    licensed_module = 'crm'
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    permission_map = crm_permission_map("calllogs")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def get_queryset(self):
        queryset = super().get_queryset().select_related(
            "lead",
            "called_by",
        )

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

        if (
            not lead.company_id
            or lead.company_id != company.id
        ):
            from rest_framework.exceptions import (
                PermissionDenied,
            )

            raise PermissionDenied(
                "You cannot log calls "
                "for this lead."
            )

        call_log = serializer.save(
            called_by=self.request.user,
        )
        log_audit(
            company=company,
            user=self.request.user,
            module='CallLogs',
            action='create',
            object_id=call_log.id,
            description=f"Call logged for lead {lead.id}.",
        )


class CallLogDetailAPIView(
    LicensedModuleMixin,
    ActionPermissionMixin,
    LeadCompanyFilteredMixin,
    RetrieveUpdateDestroyAPIView,
):
    licensed_module = 'crm'
    queryset = CallLog.objects.all()
    serializer_class = CallLogSerializer
    permission_map = crm_permission_map("calllogs")

    def perform_update(self, serializer):
        call_log = serializer.save()
        company = getattr(self.request.user, 'company', None)
        log_audit(
            company=company,
            user=self.request.user,
            module='CallLogs',
            action='update',
            object_id=call_log.id,
            description=f"Call log {call_log.id} updated.",
        )

    def perform_destroy(self, instance):
        company = getattr(self.request.user, 'company', None)
        object_id = instance.id
        instance.delete()
        log_audit(
            company=company,
            user=self.request.user,
            module='CallLogs',
            action='delete',
            object_id=object_id,
            description=f"Call log {object_id} deleted.",
        )
