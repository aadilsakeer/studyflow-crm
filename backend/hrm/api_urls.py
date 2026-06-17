from django.urls import path

from .api_views import (
    AttendanceListCreateAPIView,
    AttendanceDetailAPIView,
    LeaveRequestListCreateAPIView,
    LeaveRequestDetailAPIView,
    DepartmentListCreateAPIView,
    DepartmentDetailAPIView,
    EmployeeLetterListCreateAPIView,
    EmployeeLetterDetailAPIView,
    ResignationListCreateAPIView,
    ResignationDetailAPIView,
    PayrollListCreateAPIView,
    PayrollDetailAPIView,
)

urlpatterns = [

    path(
        'attendance/',
        AttendanceListCreateAPIView.as_view()
    ),
    path(
        'attendance/<int:pk>/',
        AttendanceDetailAPIView.as_view()
    ),

    path(
        'leave-requests/',
        LeaveRequestListCreateAPIView.as_view()
    ),
    path(
        'leave-requests/<int:pk>/',
        LeaveRequestDetailAPIView.as_view()
    ),

    path(
        'departments/',
        DepartmentListCreateAPIView.as_view()
    ),
    path(
        'departments/<int:pk>/',
        DepartmentDetailAPIView.as_view()
    ),

    path(
        'employee-letters/',
        EmployeeLetterListCreateAPIView.as_view()
    ),
    path(
        'employee-letters/<int:pk>/',
        EmployeeLetterDetailAPIView.as_view()
    ),

    path(
        'resignations/',
        ResignationListCreateAPIView.as_view()
    ),
    path(
        'resignations/<int:pk>/',
        ResignationDetailAPIView.as_view()
    ),

    path(
        'payrolls/',
        PayrollListCreateAPIView.as_view()
    ),
    path(
        'payrolls/<int:pk>/',
        PayrollDetailAPIView.as_view()
    ),
]