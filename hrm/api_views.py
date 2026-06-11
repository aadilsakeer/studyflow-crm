from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from .models import (
    Attendance,
    LeaveRequest,
    Department,
    EmployeeLetter,
    Resignation,
    Payroll
)

from .serializers import (
    AttendanceSerializer,
    LeaveRequestSerializer,
    DepartmentSerializer,
    EmployeeLetterSerializer,
    ResignationSerializer,
    PayrollSerializer
)


# Attendance

class AttendanceListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = AttendanceSerializer

    def get_queryset(self):

        return Attendance.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        attendance = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=attendance.id,
            description=(
                f'Created attendance for '
                f'{attendance.employee.username}'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class AttendanceDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = AttendanceSerializer

    def get_queryset(self):

        return Attendance.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        attendance = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=attendance.id,
            description='Updated attendance'
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description='Deleted attendance'
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)


# Leave Request

class LeaveRequestListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = LeaveRequestSerializer

    def get_queryset(self):

        return LeaveRequest.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_create(self, serializer):

        leave_request = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=leave_request.id,
            description=(
                f'Created leave request for '
                f'{leave_request.employee.username}'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class LeaveRequestDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = LeaveRequestSerializer

    def get_queryset(self):

        return LeaveRequest.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_update(self, serializer):

        leave_request = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=leave_request.id,
            description=(
                f'Updated leave request for '
                f'{leave_request.employee.username}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted leave request for '
                f'{instance.employee.username}'
            )
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class DepartmentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = DepartmentSerializer

    def get_queryset(self):

        return Department.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        department = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=department.id,
            description=(
                f'Created department '
                f'{department.name}'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class DepartmentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = DepartmentSerializer

    def get_queryset(self):

        return Department.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        department = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=department.id,
            description=(
                f'Updated department '
                f'{department.name}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted department '
                f'{instance.name}'
            )
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)

class EmployeeLetterListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = EmployeeLetterSerializer

    def get_queryset(self):

        return EmployeeLetter.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_create(self, serializer):

        letter = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=letter.id,
            description=(
                f'Created {letter.letter_type} letter'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class EmployeeLetterDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = EmployeeLetterSerializer

    def get_queryset(self):

        return EmployeeLetter.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_update(self, serializer):

        letter = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=letter.id,
            description=(
                f'Updated {letter.letter_type} letter'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted {instance.letter_type} letter'
            )
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ResignationListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ResignationSerializer

    def get_queryset(self):

        return Resignation.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_create(self, serializer):

        resignation = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=resignation.id,
            description=(
                f'Created resignation for '
                f'{resignation.employee.username}'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

class ResignationDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ResignationSerializer

    def get_queryset(self):

        return Resignation.objects.filter(
            employee__company=self.request.user.company
        )

    def perform_update(self, serializer):

        resignation = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=resignation.id,
            description=(
                f'Updated resignation for '
                f'{resignation.employee.username}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted resignation for '
                f'{instance.employee.username}'
            )
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class PayrollListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = PayrollSerializer

    def get_queryset(self):

        return Payroll.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        payroll = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='create',
            object_id=payroll.id,
            description=(
                f'Created payroll for '
                f'{payroll.employee.username}'
            )
        )

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('hrm')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PayrollDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = PayrollSerializer

    def get_queryset(self):

        return Payroll.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        payroll = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='update',
            object_id=payroll.id,
            description=(
                f'Updated payroll for '
                f'{payroll.employee.username}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='HRM',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted payroll for '
                f'{instance.employee.username}'
            )
        )

        instance.delete()

    @module_required('hrm')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('hrm')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('hrm')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('hrm')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)