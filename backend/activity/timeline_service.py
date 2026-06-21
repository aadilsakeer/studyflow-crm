from leads.models import LeadTimeline

from .models import StudentTimeline
from .timeline_constants import (
    ACTION_TO_EVENT,
    EVENT_LABELS,
    ACTIVITY_EVENT_TYPES,
)


def _user_display(user):
    if not user:
        return None

    return user.get_full_name() or user.username


def serialize_lead_event(item):
    event_type = item.event_type or ACTION_TO_EVENT.get(
        item.action,
        '',
    )

    return {
        'id': item.id,
        'event_type': event_type,
        'action': item.action,
        'description': item.description,
        'performed_by': item.performed_by_id,
        'performed_by_name': _user_display(item.performed_by),
        'created_at': item.created_at,
    }


def serialize_student_event(item):
    return {
        'id': item.id,
        'event_type': item.event_type,
        'action': item.action,
        'description': item.description,
        'performed_by': item.performed_by_id,
        'performed_by_name': _user_display(item.performed_by),
        'created_at': item.created_at,
    }


def get_lead_timeline(lead, event_type=None):
    qs = LeadTimeline.objects.filter(
        lead=lead,
    ).select_related(
        'performed_by',
    ).order_by('-created_at')

    if event_type:
        qs = qs.filter(event_type=event_type)

    return [serialize_lead_event(item) for item in qs]


def get_student_timeline(student, event_type=None):
    qs = StudentTimeline.objects.filter(
        student=student,
    ).select_related(
        'performed_by',
    ).order_by('-created_at')

    if event_type:
        qs = qs.filter(event_type=event_type)

    return [serialize_student_event(item) for item in qs]


def record_lead_event(
    lead,
    event_type,
    *,
    action=None,
    description='',
    user=None,
):
    return LeadTimeline.objects.create(
        lead=lead,
        event_type=event_type,
        action=action or EVENT_LABELS.get(
            event_type,
            event_type,
        ),
        description=description,
        performed_by=user,
    )


def record_student_event(
    student,
    event_type,
    *,
    action=None,
    description='',
    user=None,
    audit_log=None,
):
    return StudentTimeline.objects.create(
        student=student,
        event_type=event_type,
        action=action or EVENT_LABELS.get(
            event_type,
            event_type,
        ),
        description=description,
        performed_by=user,
        audit_log=audit_log,
    )


def timeline_response(entity_type, entity_id, entity_name, events):
    return {
        'entity_type': entity_type,
        'entity_id': entity_id,
        'entity_name': entity_name,
        'event_types': list(ACTIVITY_EVENT_TYPES),
        'events': events,
    }
