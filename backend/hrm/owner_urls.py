from django.urls import path

from .owner_views import (
    OwnerHRMAssetHistoryAPIView,
    OwnerHRMAssetListCreateAPIView,
    OwnerHRMAssetReturnAPIView,
    OwnerHRMAttendanceCheckInAPIView,
    OwnerHRMAttendanceCheckOutAPIView,
    OwnerHRMAttendanceListAPIView,
    OwnerHRMSDashboardAPIView,
    OwnerHRMEmployeeDetailAPIView,
    OwnerHRMEmployeeListCreateAPIView,
    OwnerHRMLeaveListCreateAPIView,
    OwnerHRMLeaveReviewAPIView,
    OwnerHRMPayrollListCreateAPIView,
    OwnerHRMPayrollStatusAPIView,
)

urlpatterns = [
    path('dashboard/', OwnerHRMSDashboardAPIView.as_view()),
    path('employees/', OwnerHRMEmployeeListCreateAPIView.as_view()),
    path('employees/<int:employee_id>/', OwnerHRMEmployeeDetailAPIView.as_view()),
    path('attendance/', OwnerHRMAttendanceListAPIView.as_view()),
    path('attendance/check-in/', OwnerHRMAttendanceCheckInAPIView.as_view()),
    path('attendance/check-out/', OwnerHRMAttendanceCheckOutAPIView.as_view()),
    path('leaves/', OwnerHRMLeaveListCreateAPIView.as_view()),
    path('leaves/<int:leave_id>/', OwnerHRMLeaveReviewAPIView.as_view()),
    path('payroll/', OwnerHRMPayrollListCreateAPIView.as_view()),
    path('payroll/<int:payroll_id>/', OwnerHRMPayrollStatusAPIView.as_view()),
    path('assets/', OwnerHRMAssetListCreateAPIView.as_view()),
    path('assets/history/', OwnerHRMAssetHistoryAPIView.as_view()),
    path('assets/<int:asset_id>/return/', OwnerHRMAssetReturnAPIView.as_view()),
]
