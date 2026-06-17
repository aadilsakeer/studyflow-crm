from django.contrib import admin

from .models import (
    Attendance,
    LeaveRequest
)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'attendance_date',
        'status',
        'check_in',
        'check_out'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'employee__username',
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):

    list_display = (
        'employee',
        'start_date',
        'end_date',
        'status'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'employee__username',
    )