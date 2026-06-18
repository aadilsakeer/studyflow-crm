from datetime import timedelta

from django.utils import timezone

from admissions.models import Application, OfferLetter, StudentDocument, VisaCase
from core.models import Company, Task
from deadlines.models import Deadline
from leads.models import FollowUp

from whatsapp.message_service import send_whatsapp_reminder
from whatsapp.templates import (
    build_document_reminder_message,
    build_follow_up_message,
    build_offer_reminder_message,
    build_visa_update_message,
)

from .notification_service import send_workflow_notification

OFFER_EXPIRY_DAYS = 7
VISA_APPOINTMENT_DAYS = 3
DEADLINE_DAYS = 7


def _counsellor_for_student(student):
    return getattr(student, 'assigned_counselor', None)


def process_follow_up_reminders(company, now, summary):
    followups = FollowUp.objects.filter(
        lead__company=company,
        lead__is_deleted=False,
        completed=False,
        follow_up_date__lte=now,
    ).select_related('lead', 'assigned_to')

    for item in followups:
        user = item.assigned_to

        if not user:
            continue

        alert_key = f'follow_up:{item.id}:{now.date()}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Follow-up Reminder',
            message=(
                f'Follow-up due for '
                f'{item.lead.first_name} {item.lead.last_name}.'
            ),
        ):
            summary['follow_up'] += 1

        wa_key = f'wa:follow_up:{item.id}:{now.date()}'

        if send_whatsapp_reminder(
            company=company,
            alert_key=wa_key,
            recipient_number=item.lead.phone,
            message=build_follow_up_message(
                item.lead,
                company.name,
            ),
            message_type='follow_up',
            lead=item.lead,
        ):
            summary['whatsapp_sent'] += 1

    tasks = Task.objects.filter(
        company=company,
        status__in=('pending', 'in_progress'),
        reminder_at__lte=now,
    ).exclude(
        reminder_at__isnull=True,
    ).select_related('assigned_to')

    for item in tasks:
        user = item.assigned_to

        if not user:
            continue

        alert_key = f'task_reminder:{item.id}:{now.date()}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Task Reminder',
            message=f'Task due: {item.title}.',
        ):
            summary['follow_up'] += 1


def process_missing_document_reminders(company, today, summary):
    documents = StudentDocument.objects.filter(
        company=company,
        is_deleted=False,
        status='requested',
    ).select_related(
        'student',
        'student__assigned_counselor',
    )

    for document in documents:
        user = _counsellor_for_student(document.student)

        if not user:
            continue

        alert_key = f'missing_document:{document.id}:{today}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Missing Document Reminder',
            message=(
                f'{document.get_document_type_display()} '
                f'missing for {document.student.student_id}.'
            ),
        ):
            summary['missing_document'] += 1

        wa_key = f'wa:missing_document:{document.id}:{today}'

        if send_whatsapp_reminder(
            company=company,
            alert_key=wa_key,
            recipient_number=document.student.lead.phone,
            message=build_document_reminder_message(
                document.student,
                document,
            ),
            message_type='document_reminder',
            lead=document.student.lead,
            student=document.student,
        ):
            summary['whatsapp_sent'] += 1


def process_offer_expiry_alerts(company, today, summary):
    cutoff = today + timedelta(days=OFFER_EXPIRY_DAYS)

    offers = OfferLetter.objects.filter(
        company=company,
        is_deleted=False,
        expiry_date__isnull=False,
        expiry_date__lte=cutoff,
        expiry_date__gte=today,
    ).exclude(
        status__in=('accepted', 'rejected', 'expired'),
    ).select_related(
        'student',
        'student__assigned_counselor',
    )

    for offer in offers:
        user = _counsellor_for_student(offer.student)

        if not user:
            continue

        alert_key = f'offer_expiry:{offer.id}:{offer.expiry_date}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Offer Expiry Alert',
            message=(
                f'Offer {offer.offer_number} expires on '
                f'{offer.expiry_date}.'
            ),
        ):
            summary['offer_expiry'] += 1

        wa_key = f'wa:offer_expiry:{offer.id}:{offer.expiry_date}'

        if send_whatsapp_reminder(
            company=company,
            alert_key=wa_key,
            recipient_number=offer.student.lead.phone,
            message=build_offer_reminder_message(
                offer.student,
                offer,
            ),
            message_type='offer_reminder',
            lead=offer.student.lead,
            student=offer.student,
        ):
            summary['whatsapp_sent'] += 1


def process_visa_appointment_reminders(company, today, summary):
    cutoff = today + timedelta(days=VISA_APPOINTMENT_DAYS)

    cases = VisaCase.objects.filter(
        company=company,
        is_deleted=False,
        appointment_date__isnull=False,
        appointment_date__gte=today,
        appointment_date__lte=cutoff,
    ).exclude(
        status__in=('approved', 'rejected'),
    ).select_related(
        'student',
        'student__assigned_counselor',
    )

    for case in cases:
        user = _counsellor_for_student(case.student)

        if not user:
            continue

        alert_key = (
            f'visa_appointment:{case.id}:{case.appointment_date}'
        )

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Visa Appointment Reminder',
            message=(
                f'Visa appointment on {case.appointment_date} '
                f'for {case.student.student_id}.'
            ),
        ):
            summary['visa_appointment'] += 1

        wa_key = (
            f'wa:visa_appointment:{case.id}:{case.appointment_date}'
        )

        if send_whatsapp_reminder(
            company=company,
            alert_key=wa_key,
            recipient_number=case.student.lead.phone,
            message=build_visa_update_message(
                case.student,
                case,
            ),
            message_type='visa_update',
            lead=case.student.lead,
            student=case.student,
        ):
            summary['whatsapp_sent'] += 1


def process_application_deadline_reminders(company, today, summary):
    cutoff = today + timedelta(days=DEADLINE_DAYS)

    deadlines = Deadline.objects.filter(
        status='pending',
        due_date__gte=today,
        due_date__lte=cutoff,
    ).select_related('student', 'student__assigned_counselor')

    deadlines = deadlines.filter(
        student__company=company,
        student__is_deleted=False,
    )

    for item in deadlines:
        user = _counsellor_for_student(item.student)

        if not user:
            continue

        alert_key = f'app_deadline:{item.id}:{item.due_date}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Application Deadline Reminder',
            message=(
                f'{item.title} due on {item.due_date} for '
                f'{item.student.student_id}.'
            ),
        ):
            summary['application_deadline'] += 1

    applications = Application.objects.filter(
        student__company=company,
        student__is_deleted=False,
        is_deleted=False,
        application_status='draft',
    ).select_related(
        'student',
        'student__assigned_counselor',
    )

    for application in applications.filter(
        created_at__date__lte=today - timedelta(days=14),
    ):
        user = _counsellor_for_student(application.student)

        if not user:
            continue

        alert_key = f'app_stale:{application.id}:{today}'

        if send_workflow_notification(
            company=company,
            user=user,
            alert_key=alert_key,
            title='Application Deadline Reminder',
            message=(
                f'Draft application for '
                f'{application.university_name} needs action.'
            ),
        ):
            summary['application_deadline'] += 1


def run_company_reminders(company):
    now = timezone.now()
    today = timezone.localdate()

    summary = {
        'company_id': company.id,
        'follow_up': 0,
        'missing_document': 0,
        'offer_expiry': 0,
        'visa_appointment': 0,
        'application_deadline': 0,
        'whatsapp_sent': 0,
    }

    process_follow_up_reminders(company, now, summary)
    process_missing_document_reminders(company, today, summary)
    process_offer_expiry_alerts(company, today, summary)
    process_visa_appointment_reminders(company, today, summary)
    process_application_deadline_reminders(company, today, summary)

    summary['total'] = sum(
        summary[key]
        for key in summary
        if key not in ('company_id', 'total', 'whatsapp_sent')
    )

    return summary


def run_all_reminders():
    results = []

    for company in Company.objects.filter(is_active=True):
        results.append(run_company_reminders(company))

    return {
        'companies_processed': len(results),
        'notifications_sent': sum(
            row.get('total', 0) for row in results
        ),
        'details': results,
    }
