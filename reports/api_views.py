from rest_framework.views import APIView
from rest_framework.response import Response

from licensing.decorators import module_required

from .services import (
    ReportService,
    FinanceReportService,
    LeadConversionReportService,
    StaffPerformanceReportService,
    CountryAnalyticsService,
    RecruitmentAnalyticsService,
    WorkVisaAnalyticsService,
)


class ReportSummaryAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = ReportService.get_summary(
            request.user.company
        )

        return Response(data)


class FinanceReportAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = FinanceReportService.get_finance_summary(
            request.user.company
        )

        return Response(data)


class LeadConversionReportAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = LeadConversionReportService.get_conversion_summary(
            request.user.company
        )

        return Response(data)


class StaffPerformanceAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = StaffPerformanceReportService.get_staff_summary(
            request.user.company
        )

        return Response(data)


class CountryAnalyticsAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = CountryAnalyticsService.get_country_summary(
            request.user.company
        )

        return Response(data)


class RecruitmentAnalyticsAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = RecruitmentAnalyticsService.get_recruitment_summary(
            request.user.company
        )

        return Response(data)


class WorkVisaAnalyticsAPIView(APIView):

    @module_required('reports')
    def get(self, request):

        data = WorkVisaAnalyticsService.get_work_visa_summary(
            request.user.company
        )

        return Response(data)