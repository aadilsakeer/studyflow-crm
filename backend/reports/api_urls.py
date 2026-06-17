from django.urls import path

from .api_views import (
    ReportSummaryAPIView,
    FinanceReportAPIView,
    LeadConversionReportAPIView,
    StaffPerformanceAPIView,
    CountryAnalyticsAPIView,
    RecruitmentAnalyticsAPIView,
    WorkVisaAnalyticsAPIView
)
urlpatterns = [

    path(
        'summary/',
        ReportSummaryAPIView.as_view(),
        name='report-summary'
    ),

    path(
        'finance/',
        FinanceReportAPIView.as_view(),
        name='finance-report'
    ),

    path(
        'lead-conversion/',
        LeadConversionReportAPIView.as_view(),
        name='lead-conversion'
    ),
    path(
    'staff-performance/',
    StaffPerformanceAPIView.as_view(),
    name='staff-performance'
),
    path(
        'country-analytics/',
        CountryAnalyticsAPIView.as_view(),
        name='country-analytics'
    ),

    path(
        'recruitment-analytics/',
        RecruitmentAnalyticsAPIView.as_view(),
        name='recruitment-analytics'
    ),
    path(
        'workvisa-analytics/',
        WorkVisaAnalyticsAPIView.as_view(),
        name='workvisa-analytics'
    ),
]