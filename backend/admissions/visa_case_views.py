from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from auditlogs.services import AuditLogService

from activity.timeline_constants import (
    EVENT_VISA_APPROVED,
    EVENT_VISA_SUBMITTED,
)
from activity.timeline_service import record_student_event

from accounts.access import filter_students_for_user
from accounts.constants import (
    PERM_VISAS_APPROVE,
    PERM_VISAS_PROCESS,
    PERM_VISAS_REJECT,
    PERM_VISAS_RESTORE,
    PERM_VISAS_SUBMIT,
)
from accounts.permissions import (
    ActionPermissionMixin,
    IsCompanyMember,
    crm_permission_map,
    permission_required,
)
from accounts.services.permission_service import user_has_permission

from .models import Student, VisaCase
from .visa_case_serializers import (
    VisaCaseSerializer,
    VisaCaseWorkflowSerializer,
)


class VisaCaseQuerysetMixin:

    def get_company(self):
        return getattr(
            self.request.user,
            'company',
            None,
        )

    def get_visa_queryset(self):
        company = self.get_company()

        if not company:
            return VisaCase.objects.none()

        allowed_students = filter_students_for_user(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        queryset = VisaCase.objects.filter(
            company=company,
            student_id__in=allowed_students,
        ).select_related(
            'student',
            'application',
            'offer_letter',
        ).prefetch_related(
            'student_documents',
        )

        for param in ('student', 'application', 'status', 'country'):
            value = self.request.query_params.get(param)

            if value:
                queryset = queryset.filter(
                    **{param: value},
                )

        return queryset.order_by('-created_at')


class VisaCaseListCreateAPIView(
    VisaCaseQuerysetMixin,
    ActionPermissionMixin,
    generics.ListCreateAPIView,
):
    permission_map = crm_permission_map('visas')
    serializer_class = VisaCaseSerializer

    def get_queryset(self):
        return self.get_visa_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_create(self, serializer):
        visa_case = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Visa Processing',
            action='create',
            object_id=visa_case.id,
            description=(
                f'Created visa case for '
                f'{visa_case.student.student_id}'
            ),
        )


class VisaCaseDetailAPIView(
    VisaCaseQuerysetMixin,
    ActionPermissionMixin,
    generics.RetrieveUpdateDestroyAPIView,
):
    permission_map = crm_permission_map('visas')
    serializer_class = VisaCaseSerializer

    def get_queryset(self):
        return self.get_visa_queryset()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    def perform_update(self, serializer):
        visa_case = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Visa Processing',
            action='update',
            object_id=visa_case.id,
            description=(
                f'Updated visa case {visa_case.id}'
            ),
        )

    def perform_destroy(self, instance):
        user = self.request.user
        instance.soft_delete(user)

        AuditLogService.log(
            company=user.company,
            user=user,
            module='Visa Processing',
            action='delete',
            object_id=instance.id,
            description=(
                f'Moved visa case {instance.id} to trash'
            ),
        )


class VisaCaseWorkflowAPIView(
    VisaCaseQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
    ]

    ACTION_PERMISSIONS = {
        'submit': PERM_VISAS_SUBMIT,
        'process': PERM_VISAS_PROCESS,
        'approve': PERM_VISAS_APPROVE,
        'reject': PERM_VISAS_REJECT,
    }

    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)

        action = kwargs.get('action')
        perm = self.ACTION_PERMISSIONS.get(action)

        if not perm:
            raise ValidationError(
                {'detail': 'Invalid action.'},
            )

        if not request.user.is_superuser and not user_has_permission(
            request.user,
            perm,
        ):
            self.permission_denied(request)

    def post(self, request, pk, *args, **kwargs):
        action = kwargs.get('action')

        visa_case = get_object_or_404(
            self.get_visa_queryset(),
            pk=pk,
        )

        serializer = VisaCaseWorkflowSerializer(
            data=request.data,
        )
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if action == 'submit':
            if visa_case.status != 'draft':
                raise ValidationError(
                    {'detail': 'Only draft cases can be submitted.'},
                )

            visa_case.status = 'submitted'

            if data.get('submission_date'):
                visa_case.submission_date = data['submission_date']
            elif not visa_case.submission_date:
                visa_case.submission_date = timezone.now().date()

            log_action = 'submit'

        elif action == 'process':
            if visa_case.status not in (
                'submitted',
                'biometrics',
            ):
                raise ValidationError(
                    {'detail': 'Case is not ready for processing.'},
                )

            if visa_case.status == 'submitted':
                visa_case.status = 'biometrics'
            else:
                visa_case.status = 'processing'

            if data.get('appointment_date'):
                visa_case.appointment_date = data['appointment_date']

            if data.get('submission_date'):
                visa_case.submission_date = data['submission_date']

            log_action = 'process'

        elif action == 'approve':
            if visa_case.status not in (
                'submitted',
                'biometrics',
                'processing',
            ):
                raise ValidationError(
                    {'detail': 'Case cannot be approved.'},
                )

            visa_case.status = 'approved'

            if data.get('decision_date'):
                visa_case.decision_date = data['decision_date']
            elif not visa_case.decision_date:
                visa_case.decision_date = timezone.now().date()

            if data.get('visa_number'):
                visa_case.visa_number = data['visa_number']

            log_action = 'approve'

        elif action == 'reject':
            if visa_case.status in (
                'approved',
                'rejected',
            ):
                raise ValidationError(
                    {'detail': 'Case is already finalized.'},
                )

            visa_case.status = 'rejected'

            if data.get('decision_date'):
                visa_case.decision_date = data['decision_date']
            elif not visa_case.decision_date:
                visa_case.decision_date = timezone.now().date()

            log_action = 'reject'

        if data.get('notes'):
            visa_case.notes = data['notes']

        visa_case.save()

        AuditLogService.log(
            company=request.user.company,
            user=request.user,
            module='Visa Processing',
            action=log_action,
            object_id=visa_case.id,
            description=(
                f'{log_action.title()} visa case '
                f'{visa_case.id}'
            ),
        )

        if action == 'submit':
            record_student_event(
                visa_case.student,
                EVENT_VISA_SUBMITTED,
                description=(
                    f'Visa application submitted for '
                    f'{visa_case.country}.'
                ),
                user=request.user,
            )
        elif action == 'approve':
            record_student_event(
                visa_case.student,
                EVENT_VISA_APPROVED,
                description=(
                    f'Visa approved for {visa_case.country}.'
                ),
                user=request.user,
            )

        return Response(
            VisaCaseSerializer(
                visa_case,
                context={'request': request},
            ).data,
        )


class VisaCaseTrashListAPIView(
    VisaCaseQuerysetMixin,
    ActionPermissionMixin,
    generics.ListAPIView,
):
    permission_map = {'GET': 'visas.restore'}
    serializer_class = VisaCaseSerializer

    def get_queryset(self):
        company = self.get_company()

        if not company:
            return VisaCase.all_objects.none()

        allowed_students = filter_students_for_user(
            Student.all_objects.filter(
                company=company,
                is_deleted=False,
            ),
            self.request.user,
        ).values_list('pk', flat=True)

        return VisaCase.all_objects.filter(
            company=company,
            student_id__in=allowed_students,
            is_deleted=True,
        ).select_related(
            'student',
            'application',
            'offer_letter',
        ).prefetch_related(
            'student_documents',
        ).order_by('-deleted_at')


class VisaCaseRestoreAPIView(
    VisaCaseQuerysetMixin,
    APIView,
):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_VISAS_RESTORE),
    ]

    def post(self, request, pk):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {'detail': 'Company not found.'},
            )

        allowed_students = filter_students_for_user(
            Student.all_objects.filter(
                company=company,
                is_deleted=False,
            ),
            request.user,
        ).values_list('pk', flat=True)

        visa_case = get_object_or_404(
            VisaCase.all_objects.filter(
                company=company,
                student_id__in=allowed_students,
                is_deleted=True,
            ),
            pk=pk,
        )

        visa_case.restore()

        AuditLogService.log(
            company=company,
            user=request.user,
            module='Visa Processing',
            action='restore',
            object_id=visa_case.id,
            description=(
                f'Restored visa case {visa_case.id}'
            ),
        )

        return Response(
            VisaCaseSerializer(
                visa_case,
                context={'request': request},
            ).data,
            status=status.HTTP_200_OK,
        )
