from django.db.models import Q
from django.utils import timezone

from accounts.constants import (
    ROLE_ADMIN,
    ROLE_COUNSELLOR,
    ROLE_MANAGER,
    ROLE_TELECALLER,
    ROLE_VISA_TEAM,
)

from admissions.models import Student
from leads.models import Lead

from .models import Task

STAFF_ROLES = (
    ROLE_TELECALLER,
    ROLE_COUNSELLOR,
    ROLE_VISA_TEAM,
)


def filter_tasks_for_user(queryset, user):
    if not user or not user.is_authenticated:
        return queryset.none()

    if user.is_superuser:
        return queryset

    role = getattr(getattr(user, 'role', None), 'name', None)

    if role in (ROLE_ADMIN, ROLE_MANAGER):
        return queryset

    if role in STAFF_ROLES:
        return queryset.filter(
            Q(assigned_to=user) | Q(assigned_by=user),
        )

    return queryset.filter(assigned_to=user)


def validate_task_links(company, lead=None, student=None):
    if lead and lead.company_id != company.id:
        raise ValueError('Lead not in your company.')

    if student and student.company_id != company.id:
        raise ValueError('Student not in your company.')


def create_task(
    company,
    user,
    *,
    title,
    task_type='general_task',
    assigned_to=None,
    due_date=None,
    priority='medium',
    status='pending',
    notes='',
    description='',
    lead=None,
    student=None,
    reminder_at=None,
):
    validate_task_links(company, lead, student)

    return Task.objects.create(
        company=company,
        title=title,
        task_type=task_type,
        assigned_to=assigned_to,
        assigned_by=user,
        due_date=due_date,
        priority=priority,
        status=status,
        notes=notes,
        description=description,
        lead=lead,
        student=student,
        reminder_at=reminder_at,
    )


def update_task(task, user, data):
    allowed = (
        'title',
        'task_type',
        'assigned_to',
        'due_date',
        'priority',
        'status',
        'notes',
        'description',
        'lead',
        'student',
        'reminder_at',
    )

    for field in allowed:
        if field in data:
            setattr(task, field, data[field])

    if task.lead_id:
        validate_task_links(task.company, lead=task.lead)

    if task.student_id:
        validate_task_links(task.company, student=task.student)

    if task.status == 'completed' and not task.completed_at:
        task.completed_at = timezone.now()
    elif task.status != 'completed':
        task.completed_at = None

    task.save()
    return task


def get_task_summary(company, user):
    today = timezone.localdate()
    now = timezone.now()

    qs = Task.objects.filter(company=company)
    qs = filter_tasks_for_user(qs, user)

    open_qs = qs.exclude(status__in=('completed', 'cancelled'))

    return {
        'todays_tasks': open_qs.filter(
            due_date__date=today,
        ).count(),
        'pending_tasks': open_qs.filter(
            status='pending',
        ).count(),
        'overdue_tasks': open_qs.filter(
            due_date__lt=now,
        ).count(),
        'completed_today': qs.filter(
            status='completed',
            completed_at__date=today,
        ).count(),
        'completed_today_tasks': qs.filter(
            status='completed',
            completed_at__date=today,
        ).count(),
        'due_reminders': open_qs.filter(
            reminder_at__lte=now,
        ).exclude(
            reminder_at__isnull=True,
        ).count(),
    }


def resolve_lead(company, lead_id):
    if not lead_id:
        return None

    return Lead.objects.filter(
        company=company,
        is_deleted=False,
        pk=lead_id,
    ).first()


def resolve_student(company, student_id):
    if not student_id:
        return None

    return Student.objects.filter(
        company=company,
        is_deleted=False,
        pk=student_id,
    ).first()
