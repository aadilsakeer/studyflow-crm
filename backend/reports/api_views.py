from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from licensing.decorators import module_required

from accounts.constants import PERM_REPORTS_VIEW
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from .services import (
    ReportService,
    FinanceReportService,
    LeadConversionReportService,
    StaffPerformanceReportService,
    CountryAnalyticsService,
    RecruitmentAnalyticsService,
    WorkVisaAnalyticsService,
)


class LicensedReportAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_REPORTS_VIEW),
    ]


class ReportSummaryAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = ReportService.get_summary(
            request.user.company
        )

        return Response(data)


class FinanceReportAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = FinanceReportService.get_finance_summary(
            request.user.company
        )

        return Response(data)


class LeadConversionReportAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = LeadConversionReportService.get_conversion_summary(
            request.user.company
        )

        return Response(data)


class StaffPerformanceAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = StaffPerformanceReportService.get_staff_summary(
            request.user.company
        )

        return Response(data)


class CountryAnalyticsAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = CountryAnalyticsService.get_country_summary(
            request.user.company
        )

        return Response(data)


class RecruitmentAnalyticsAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = RecruitmentAnalyticsService.get_recruitment_summary(
            request.user.company
        )

        return Response(data)


class WorkVisaAnalyticsAPIView(LicensedReportAPIView):

    @module_required('reports')
    def get(self, request):

        data = WorkVisaAnalyticsService.get_work_visa_summary(
            request.user.company
        )

        return Response(data)
