from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError

from admissions.models import Student
from admissions.serializers import (
    StudentSerializer,
)

from accounts.access import filter_leads_for_user
from accounts.constants import (
    PERM_LEADS_CONVERT,
    PERM_LEADS_RESTORE,
)
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
    ActionPermissionMixin,
    crm_permission_map,
)

from core.mixins import (
    CompanyCreateMixin,
)

from auditlogs.helpers import log_audit

from .models import Lead, LeadTimeline, LeadAuditLog
from .serializers import LeadSerializer
from .timeline_serializers import (
    LeadTimelineSerializer,
)
from .audit_serializers import (
    LeadAuditLogSerializer,
)
from .audit_service import (
    snapshot_lead,
    log_lead_created,
    log_lead_changes,
)
from licensing.usage_service import UsageLimitService
from licensing.constants import LIMIT_LEADS, LIMIT_STUDENTS

from .conversion_service import (
    convert_lead_to_student,
)


class LeadQuerysetMixin:
    def get_company(self):
        return getattr(
            self.request.user,
            "company",
            None,
        )

    def get_lead_queryset(self):
        company = self.get_company()

        if not company:
            return Lead.objects.none()

        queryset = Lead.objects.filter(
            company=company,
            company__isnull=False,
        )

        return filter_leads_for_user(
            queryset,
            self.request.user,
        )


class LeadListAPIView(
    LeadQuerysetMixin,
    ActionPermissionMixin,
    CompanyCreateMixin,
    ListCreateAPIView,
):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_map = crm_permission_map("leads")

    def get_queryset(self):
        queryset = self.get_lead_queryset().select_related(
            "company",
            "branch",
            "source",
            "assigned_to",
        ).prefetch_related("tags")

        search = self.request.query_params.get(
            "search",
        )
        status = self.request.query_params.get(
            "status",
        )
        assigned_to = self.request.query_params.get(
            "assigned_to",
        )
        mine = self.request.query_params.get(
            "mine",
        )

        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(phone__icontains=search)
                | Q(email__icontains=search)
            )

        if status:
            queryset = queryset.filter(
                status=status,
            )

        if mine and mine.lower() == "true":
            queryset = queryset.filter(
                assigned_to=self.request.user,
            )
        elif assigned_to:
            queryset = queryset.filter(
                assigned_to_id=assigned_to,
            )

        return queryset.order_by("-created_at")

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        company = self.request.user.company
        UsageLimitService.check(company, LIMIT_LEADS)
        super().perform_create(serializer)
        lead = serializer.instance
        log_lead_created(lead, self.request.user)
        log_audit(
            company=lead.company,
            user=self.request.user,
            module='Leads',
            action='create',
            object_id=lead.id,
            description=(
                f"Lead {lead.first_name} {lead.last_name} created."
            ),
        )


class LeadDetailAPIView(
    LeadQuerysetMixin,
    ActionPermissionMixin,
    RetrieveUpdateDestroyAPIView,
):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    permission_map = crm_permission_map("leads")

    def get_queryset(self):
        return self.get_lead_queryset()

    def perform_update(self, serializer):
        instance = serializer.instance
        old_snapshot = snapshot_lead(instance)
        lead = serializer.save()

        log_lead_changes(
            lead,
            old_snapshot,
            self.request.user,
        )
        log_audit(
            company=lead.company,
            user=self.request.user,
            module='Leads',
            action='update',
            object_id=lead.id,
            description=f"Lead {lead.first_name} {lead.last_name} updated.",
        )

    def perform_destroy(self, instance):
        if Student.objects.filter(
            lead=instance,
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "Cannot delete a lead that "
                        "has a student record."
                    ),
                },
            )

        user = self.request.user
        instance.soft_delete(user)

        LeadTimeline.objects.create(
            lead=instance,
            action="deleted",
            description="Lead moved to trash",
            performed_by=user,
        )
        LeadAuditLog.objects.create(
            lead=instance,
            field_changed="is_deleted",
            old_value="False",
            new_value="True",
            changed_by=user,
        )
        log_audit(
            company=instance.company,
            user=user,
            module='Leads',
            action='delete',
            object_id=instance.id,
            description=(
                f"Lead {instance.first_name} "
                f"{instance.last_name} deleted."
            ),
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class LeadTimelineListAPIView(
    LeadQuerysetMixin,
    ActionPermissionMixin,
    ListAPIView,
):
    serializer_class = LeadTimelineSerializer
    permission_map = {"GET": "leads.view"}

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return LeadTimeline.objects.none()

        lead_pk = self.kwargs["lead_pk"]

        if not self.get_lead_queryset().filter(
            pk=lead_pk,
        ).exists():
            return LeadTimeline.objects.none()

        qs = LeadTimeline.objects.filter(
            lead_id=lead_pk,
            lead__company=company,
        ).select_related(
            "performed_by",
            "lead",
        ).order_by("-created_at")

        event_type = self.request.query_params.get('event_type')

        if event_type:
            qs = qs.filter(event_type=event_type)

        return qs


class LeadAuditLogListAPIView(
    LeadQuerysetMixin,
    ActionPermissionMixin,
    ListAPIView,
):
    serializer_class = LeadAuditLogSerializer
    permission_map = {"GET": "leads.view"}

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return LeadAuditLog.objects.none()

        lead_pk = self.kwargs["lead_pk"]

        if not self.get_lead_queryset().filter(
            pk=lead_pk,
        ).exists():
            return LeadAuditLog.objects.none()

        return LeadAuditLog.objects.filter(
            lead_id=lead_pk,
            lead__company=company,
        ).select_related(
            "changed_by",
            "lead",
        ).order_by("-changed_at")


class LeadConvertAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_CONVERT),
    ]

    def post(self, request, pk):
        company = self.get_company()

        if not company:
            return Response(
                {
                    "detail": (
                        "Your account is not linked "
                        "to a company."
                    ),
                },
                status=400,
            )

        lead = get_object_or_404(
            self.get_lead_queryset(),
            pk=pk,
        )

        student = convert_lead_to_student(
            lead,
            request.user,
        )

        serializer = StudentSerializer(
            student,
        )

        return Response(
            serializer.data,
            status=201,
        )


class LeadTrashListAPIView(
    LeadQuerysetMixin,
    ActionPermissionMixin,
    ListAPIView,
):
    serializer_class = LeadSerializer
    permission_map = {"GET": "leads.restore"}

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return Lead.all_objects.none()

        queryset = Lead.all_objects.dead().filter(
            company=company,
        )

        return filter_leads_for_user(
            queryset,
            self.request.user,
        ).select_related(
            "branch",
            "source",
            "assigned_to",
            "assigned_counsellor",
        ).prefetch_related(
            "tags",
        ).order_by("-deleted_at")


class LeadRestoreAPIView(
    LeadQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_LEADS_RESTORE),
    ]

    def post(self, request, pk):
        company = self.get_company()

        if not company:
            return Response(
                {"detail": "Company not found."},
                status=400,
            )

        lead = get_object_or_404(
            Lead.all_objects.dead().filter(
                company=company,
            ),
            pk=pk,
        )

        if Lead.objects.filter(
            company=company,
            phone=lead.phone,
        ).exists():
            raise ValidationError(
                {
                    "detail": (
                        "An active lead with this "
                        "phone already exists."
                    ),
                },
            )

        lead.restore()

        LeadTimeline.objects.create(
            lead=lead,
            action="restored",
            description="Lead restored from trash",
            performed_by=request.user,
        )
        LeadAuditLog.objects.create(
            lead=lead,
            field_changed="is_deleted",
            old_value="True",
            new_value="False",
            changed_by=request.user,
        )
        log_audit(
            company=company,
            user=request.user,
            module='Leads',
            action='restore',
            object_id=lead.id,
            description=(
                f"Lead {lead.first_name} {lead.last_name} restored."
            ),
        )

        return Response(
            LeadSerializer(lead).data,
        )
