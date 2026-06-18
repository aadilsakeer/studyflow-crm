from django.utils import timezone

from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_TASKS_VIEW
from accounts.permissions import (
    ActionPermissionMixin,
    IsCompanyMember,
    crm_permission_map,
    permission_required,
)

from auditlogs.services import AuditLogService

from .models import Task
from .task_serializers import TaskSerializer
from .task_service import (
    create_task,
    filter_tasks_for_user,
    get_task_summary,
    resolve_lead,
    resolve_student,
    update_task,
)


class TaskQuerysetMixin:

    def get_company(self):
        return getattr(self.request.user, 'company', None)

    def get_task_queryset(self):
        company = self.get_company()

        if not company:
            return Task.objects.none()

        queryset = Task.objects.filter(
            company=company,
        ).select_related(
            'assigned_to',
            'assigned_by',
            'lead',
            'student',
        )

        queryset = filter_tasks_for_user(
            queryset,
            self.request.user,
        )

        params = self.request.query_params

        for key, field in (
            ('status', 'status'),
            ('priority', 'priority'),
            ('task_type', 'task_type'),
            ('assigned_to', 'assigned_to'),
            ('lead', 'lead_id'),
            ('student', 'student_id'),
        ):
            value = params.get(key)

            if value:
                queryset = queryset.filter(**{field: value})

        if params.get('overdue') == 'true':
            queryset = queryset.filter(
                due_date__lt=timezone.now(),
            ).exclude(
                status__in=('completed', 'cancelled'),
            )

        if params.get('due_today') == 'true':
            queryset = queryset.filter(
                due_date__date=timezone.localdate(),
            )

        if params.get('completed_today') == 'true':
            queryset = queryset.filter(
                status='completed',
                completed_at__date=timezone.localdate(),
            )

        if params.get('reminder_due') == 'true':
            queryset = queryset.filter(
                reminder_at__lte=timezone.now(),
            ).exclude(
                status__in=('completed', 'cancelled'),
            )

        return queryset.order_by('-due_date', '-created_at')


class TaskListCreateAPIView(
    TaskQuerysetMixin,
    ActionPermissionMixin,
    ListCreateAPIView,
):
    serializer_class = TaskSerializer
    permission_map = crm_permission_map('tasks')

    def get_queryset(self):
        return self.get_task_queryset()

    def perform_create(self, serializer):
        company = self.get_company()

        if not company:
            raise ValidationError(
                {'detail': 'Company required.'},
            )

        lead = resolve_lead(
            company,
            self.request.data.get('lead'),
        )
        student = resolve_student(
            company,
            self.request.data.get('student'),
        )

        task = create_task(
            company,
            self.request.user,
            title=serializer.validated_data['title'],
            task_type=serializer.validated_data.get(
                'task_type',
                'general_task',
            ),
            assigned_to=serializer.validated_data.get(
                'assigned_to',
            ),
            due_date=serializer.validated_data.get('due_date'),
            priority=serializer.validated_data.get(
                'priority',
                'medium',
            ),
            status=serializer.validated_data.get(
                'status',
                'pending',
            ),
            notes=serializer.validated_data.get('notes', ''),
            description=serializer.validated_data.get(
                'description',
                '',
            ),
            lead=lead,
            student=student,
            reminder_at=serializer.validated_data.get(
                'reminder_at',
            ),
        )

        AuditLogService.log(
            company=company,
            user=self.request.user,
            module='Tasks',
            action='create',
            object_id=task.id,
            description=f'Created task {task.title}',
        )

        serializer.instance = task


class TaskDetailAPIView(
    TaskQuerysetMixin,
    ActionPermissionMixin,
    RetrieveUpdateDestroyAPIView,
):
    serializer_class = TaskSerializer
    permission_map = crm_permission_map('tasks')

    def get_queryset(self):
        return self.get_task_queryset()

    def perform_update(self, serializer):
        task = serializer.instance
        company = self.get_company()

        data = serializer.validated_data.copy()

        if 'lead' in self.request.data:
            data['lead'] = resolve_lead(
                company,
                self.request.data.get('lead'),
            )

        if 'student' in self.request.data:
            data['student'] = resolve_student(
                company,
                self.request.data.get('student'),
            )

        update_task(task, self.request.user, data)
        task.refresh_from_db()

        AuditLogService.log(
            company=company,
            user=self.request.user,
            module='Tasks',
            action='update',
            object_id=task.id,
            description=f'Updated task {task.title}',
        )

        serializer.instance = task

    def perform_destroy(self, instance):
        company = self.get_company()

        AuditLogService.log(
            company=company,
            user=self.request.user,
            module='Tasks',
            action='delete',
            object_id=instance.id,
            description=f'Deleted task {instance.title}',
        )

        instance.delete()


class TaskSummaryAPIView(TaskQuerysetMixin, APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_TASKS_VIEW),
    ]

    def get(self, request):
        company = self.get_company()

        if not company:
            raise NotFound('Company not found.')

        return Response(
            get_task_summary(company, request.user),
        )
