from django.db.models import Q

from leads.models import CallLog

from whatsapp.models import WhatsAppMessage

from .models import CommunicationNote, EmailLog, WhatsAppLog


def _user_display(user):
    if not user:
        return None

    return user.get_full_name() or user.username


def _resolve_lead(*, lead=None, student=None):
    if lead:
        return lead

    if student:
        return student.lead

    return None


def _note_queryset(*, company, lead=None, student=None):
    qs = CommunicationNote.objects.filter(
        company=company,
    ).select_related(
        'author',
        'lead',
        'student',
    )

    if student:
        qs = qs.filter(
            Q(student=student)
            | Q(lead=student.lead),
        )
    elif lead:
        qs = qs.filter(
            Q(lead=lead)
            | Q(student__lead=lead),
        )

    return qs


def _email_queryset(*, company, lead=None, student=None):
    qs = EmailLog.objects.filter(
        company=company,
    ).select_related(
        'logged_by',
        'lead',
        'student',
    )

    if student:
        qs = qs.filter(
            Q(student=student)
            | Q(lead=student.lead),
        )
    elif lead:
        qs = qs.filter(
            Q(lead=lead)
            | Q(student__lead=lead),
        )

    return qs


def _whatsapp_log_queryset(*, company, lead=None, student=None):
    qs = WhatsAppLog.objects.filter(
        company=company,
    ).select_related(
        'logged_by',
        'lead',
        'student',
    )

    if student:
        qs = qs.filter(
            Q(student=student)
            | Q(lead=student.lead),
        )
    elif lead:
        qs = qs.filter(
            Q(lead=lead)
            | Q(student__lead=lead),
        )

    return qs


def _whatsapp_message_queryset(*, company, lead=None, student=None):
    lead = _resolve_lead(
        lead=lead,
        student=student,
    )

    if not lead:
        return WhatsAppMessage.objects.none()

    qs = WhatsAppMessage.objects.filter(
        company=company,
    ).select_related(
        'account',
        'account__user',
    )

    return qs.filter(
        Q(lead=lead)
        | Q(student__lead=lead)
        | Q(recipient_number=lead.phone)
        | Q(recipient_number__endswith=lead.phone[-10:]),
    )


def _serialize_call(item):
    return {
        'id': item.id,
        'type': 'call',
        'timestamp': item.call_time,
        'title': item.outcome,
        'summary': item.notes,
        'author_name': _user_display(item.called_by),
        'meta': {},
    }


def _serialize_note(item):
    return {
        'id': item.id,
        'type': 'note',
        'timestamp': item.created_at,
        'title': 'Note',
        'summary': item.content,
        'author_name': _user_display(item.author),
        'meta': {},
    }


def _serialize_email(item):
    return {
        'id': item.id,
        'type': 'email',
        'timestamp': item.sent_at,
        'title': item.subject,
        'summary': item.body,
        'author_name': _user_display(item.logged_by),
        'meta': {
            'recipient_email': item.recipient_email,
            'direction': item.direction,
        },
    }


def _serialize_whatsapp_log(item):
    return {
        'id': item.id,
        'type': 'whatsapp',
        'timestamp': item.created_at,
        'title': f'WhatsApp ({item.get_direction_display()})',
        'summary': item.message,
        'author_name': _user_display(item.logged_by),
        'meta': {
            'contact_number': item.contact_number,
            'direction': item.direction,
        },
    }


def _serialize_whatsapp_message(item):
    sender = None

    if item.account and item.account.user:
        sender = item.account.user

    return {
        'id': item.id,
        'type': 'whatsapp',
        'timestamp': item.created_at,
        'title': f'WhatsApp ({item.get_status_display()})',
        'summary': item.message,
        'author_name': _user_display(sender),
        'meta': {
            'contact_number': item.recipient_number,
            'status': item.status,
        },
    }


def get_communication_history(
    *,
    company,
    lead=None,
    student=None,
    limit=100,
):
    resolved_lead = _resolve_lead(
        lead=lead,
        student=student,
    )

    entries = []

    if resolved_lead:
        for item in CallLog.objects.filter(
            lead=resolved_lead,
        ).select_related('called_by'):
            entries.append(_serialize_call(item))

    for item in _note_queryset(
        company=company,
        lead=lead,
        student=student,
    ):
        entries.append(_serialize_note(item))

    for item in _email_queryset(
        company=company,
        lead=lead,
        student=student,
    ):
        entries.append(_serialize_email(item))

    for item in _whatsapp_log_queryset(
        company=company,
        lead=lead,
        student=student,
    ):
        entries.append(_serialize_whatsapp_log(item))

    for item in _whatsapp_message_queryset(
        company=company,
        lead=lead,
        student=student,
    ):
        entries.append(_serialize_whatsapp_message(item))

    entries.sort(
        key=lambda row: row['timestamp'],
        reverse=True,
    )

    return entries[:limit]


def get_company_communication_history(
    *,
    company,
    comm_type=None,
    limit=100,
):
    entries = []

    if not comm_type or comm_type == 'call':
        for item in CallLog.objects.filter(
            lead__company=company,
            lead__is_deleted=False,
        ).select_related(
            'called_by',
            'lead',
        ).order_by('-call_time')[:limit]:
            row = _serialize_call(item)
            row['meta']['lead_id'] = item.lead_id
            row['meta']['lead_name'] = (
                f'{item.lead.first_name} '
                f'{item.lead.last_name}'.strip()
            )
            entries.append(row)

    if not comm_type or comm_type == 'note':
        for item in CommunicationNote.objects.filter(
            company=company,
        ).select_related(
            'author',
            'lead',
            'student',
        ).order_by('-created_at')[:limit]:
            row = _serialize_note(item)
            row['meta']['lead_id'] = item.lead_id
            row['meta']['student_id'] = item.student_id
            entries.append(row)

    if not comm_type or comm_type == 'email':
        for item in EmailLog.objects.filter(
            company=company,
        ).select_related(
            'logged_by',
            'lead',
            'student',
        ).order_by('-sent_at')[:limit]:
            row = _serialize_email(item)
            row['meta']['lead_id'] = item.lead_id
            row['meta']['student_id'] = item.student_id
            entries.append(row)

    if not comm_type or comm_type == 'whatsapp':
        for item in WhatsAppLog.objects.filter(
            company=company,
        ).select_related(
            'logged_by',
            'lead',
            'student',
        ).order_by('-created_at')[:limit]:
            row = _serialize_whatsapp_log(item)
            row['meta']['lead_id'] = item.lead_id
            row['meta']['student_id'] = item.student_id
            entries.append(row)

        for item in WhatsAppMessage.objects.filter(
            company=company,
        ).select_related(
            'account',
            'account__user',
        ).order_by('-created_at')[:limit]:
            entries.append(
                _serialize_whatsapp_message(item),
            )

    entries.sort(
        key=lambda row: row['timestamp'],
        reverse=True,
    )

    return entries[:limit]
