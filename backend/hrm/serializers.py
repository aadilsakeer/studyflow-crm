from rest_framework import serializers

from .models import (
    Attendance,
    LeaveRequest,
    EmployeeLetter,
    Resignation,
    Department,
    Payroll
)


class AttendanceSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Attendance
        fields = (
            "id",
            "company",
            "employee",
            "attendance_date",
            "status",
            "check_in",
            "check_out",
            "remarks",
        )
        read_only_fields = (
            "company",
        )


class LeaveRequestSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = LeaveRequest
        fields = (
            "id",
            "employee",
            "start_date",
            "end_date",
            "reason",
            "status",
            "applied_at",
        )
        read_only_fields = (
            "applied_at",
        )


class EmployeeLetterSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EmployeeLetter
        fields = (
            "id",
            "employee",
            "letter_type",
            "issue_date",
            "subject",
            "content",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )


class ResignationSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Resignation
        fields = (
            "id",
            "employee",
            "resignation_date",
            "last_working_day",
            "reason",
            "status",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )


class DepartmentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Department
        fields = (
            "id",
            "company",
            "name",
            "description",
        )
        read_only_fields = (
            "company",
        )


class PayrollSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Payroll
        fields = (
            "id",
            "company",
            "employee",
            "month",
            "year",
            "basic_salary",
            "deductions",
            "net_salary",
            "status",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )
