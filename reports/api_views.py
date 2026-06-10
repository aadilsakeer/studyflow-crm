from rest_framework.views import APIView
from rest_framework.response import Response

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

    def get(self, request):

        data = ReportService.get_summary()

        return Response(data)


class FinanceReportAPIView(APIView):

    def get(self, request):

        data = FinanceReportService.get_finance_summary()

        return Response(data)


class LeadConversionReportAPIView(APIView):

    def get(self, request):

        data = LeadConversionReportService.get_conversion_summary()

        return Response(data)
    
class StaffPerformanceAPIView(APIView):

    def get(self, request):

        data = StaffPerformanceReportService.get_staff_summary()

        return Response(data)

class CountryAnalyticsAPIView(APIView):

    def get(self, request):

        data = CountryAnalyticsService.get_country_summary()

        return Response(data)
    
class RecruitmentAnalyticsAPIView(APIView):

    def get(self, request):

        data = RecruitmentAnalyticsService.get_recruitment_summary()

        return Response(data)

class WorkVisaAnalyticsAPIView(APIView):

    def get(self, request):

        data = WorkVisaAnalyticsService.get_work_visa_summary()

        return Response(data)