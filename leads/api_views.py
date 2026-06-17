from django.db.models import Q
from django.shortcuts import get_object_or_404

from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
    ListAPIView,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import (
    PageNumberPagination,
)

from admissions.serializers import (
    StudentSerializer,
)

from core.mixins import (
    CompanyCreateMixin,
)

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
from .conversion_service import (
    convert_lead_to_student,
)


class LeadPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class LeadListAPIView(
    CompanyCreateMixin,
    ListCreateAPIView,
):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer
    pagination_class = LeadPagination

    def get_queryset(self):
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return Lead.objects.none()

        queryset = Lead.objects.filter(
            Q(company=company)
            | Q(company__isnull=True)
        )

        search = self.request.query_params.get(
            "search",
        )
        status = self.request.query_params.get(
            "status",
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

        return queryset.order_by("-created_at")
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    def perform_create(self, serializer):
        super().perform_create(serializer)
        log_lead_created(
            serializer.instance,
            self.request.user,
        )


class LeadDetailAPIView(
    RetrieveUpdateDestroyAPIView,
):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer

    def get_queryset(self):
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return Lead.objects.none()

        return Lead.objects.filter(
            Q(company=company)
            | Q(company__isnull=True)
        )

    def perform_update(self, serializer):
        instance = serializer.instance
        old_snapshot = snapshot_lead(instance)

        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if (
            company
            and instance.company_id is None
        ):
            lead = serializer.save(
                company=company,
            )
        else:
            lead = serializer.save()

        log_lead_changes(
            lead,
            old_snapshot,
            self.request.user,
        )

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context


class LeadTimelineListAPIView(ListAPIView):
    serializer_class = LeadTimelineSerializer

    def get_queryset(self):
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return LeadTimeline.objects.none()

        lead_pk = self.kwargs["lead_pk"]

        return LeadTimeline.objects.filter(
            lead_id=lead_pk,
            lead__company=company,
        ).order_by("-created_at")


class LeadAuditLogListAPIView(ListAPIView):
    serializer_class = LeadAuditLogSerializer

    def get_queryset(self):
        company = getattr(
            self.request.user,
            "company",
            None,
        )

        if not company:
            return LeadAuditLog.objects.none()

        lead_pk = self.kwargs["lead_pk"]

        return LeadAuditLog.objects.filter(
            lead_id=lead_pk,
            lead__company=company,
        ).order_by("-changed_at")


class LeadConvertAPIView(APIView):

    def post(self, request, pk):
        company = getattr(
            request.user,
            "company",
            None,
        )

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
            Lead.objects.filter(
                Q(company=company)
                | Q(company__isnull=True)
            ),
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
