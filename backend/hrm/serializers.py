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
        fields = '__all__'


class LeaveRequestSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = LeaveRequest
        fields = '__all__'


class EmployeeLetterSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = EmployeeLetter
        fields = '__all__'


class ResignationSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Resignation
        fields = '__all__'


class DepartmentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Department
        fields = '__all__'


class PayrollSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Payroll
        fields = '__all__'