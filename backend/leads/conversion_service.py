from django.db import transaction

from rest_framework.exceptions import ValidationError

from activity.timeline_constants import EVENT_STUDENT_CONVERTED
from activity.timeline_service import (
    record_lead_event,
    record_student_event,
)

from admissions.models import Student
from leads.models import Lead


CONVERTIBLE_LEAD_STATUSES = frozenset({
    'interested',
    'qualified',
    'documents_requested',
    'documents_received',
    'counsellor_assigned',
    'profile_evaluation',
    'university_selection',
    'application_ready',
})

NON_CONVERTIBLE_LEAD_STATUSES = frozenset({
    'new',
    'assigned',
    'called',
    'not_interested',
    'follow_up',
    'lost',
    'converted',
})


def can_convert_lead_status(status):
    return status in CONVERTIBLE_LEAD_STATUSES


def generate_student_id(company):
    count = Student.all_objects.filter(
        company=company,
    ).count()

    return f"STU-{company.id:03d}-{count + 1:05d}"


@transaction.atomic
def convert_lead_to_student(lead, user):
    if lead.is_deleted:
        raise ValidationError(
            {
                "detail": "Cannot convert a deleted lead.",
            },
        )

    if lead.status == "converted":
        raise ValidationError(
            {
                "detail": (
                    "This lead is already "
                    "converted."
                ),
            }
        )

    if Student.objects.filter(
        lead=lead,
    ).exists():
        raise ValidationError(
            {
                "detail": (
                    "A student record already "
                    "exists for this lead."
                ),
            }
        )

    company = user.company

    if not company:
        raise ValidationError(
            {
                "detail": (
                    "Your account is not linked "
                    "to a company."
                ),
            }
        )

    if lead.company_id and lead.company_id != company.id:
        raise ValidationError(
            {
                "detail": (
                    "You cannot convert leads "
                    "from another company."
                ),
            }
        )

    from licensing.constants import LIMIT_STUDENTS
    from licensing.usage_service import UsageLimitService

    UsageLimitService.check(company, LIMIT_STUDENTS)

    if not can_convert_lead_status(lead.status):
        raise ValidationError(
            {
                "detail": (
                    "Lead cannot be converted from its "
                    f"current status ({lead.get_status_display()}). "
                    "Move the lead to Interested, Qualified, "
                    "or a counsellor pipeline stage first."
                ),
            },
        )

    student = Student.objects.create(
        lead=lead,
        company=company,
        student_id=generate_student_id(
            company,
        ),
        destination_country=(
            lead.country_interest or ""
        ),
        assigned_counselor=user,
        notes=lead.remarks or "",
    )

    if not lead.company_id:
        lead.company = company

    lead.status = "converted"
    lead.save()

    record_lead_event(
        lead,
        EVENT_STUDENT_CONVERTED,
        description=(
            f"Lead converted to student "
            f"{student.student_id}."
        ),
        user=user,
    )

    record_student_event(
        student,
        EVENT_STUDENT_CONVERTED,
        description=(
            f"Converted from lead "
            f"{lead.first_name} {lead.last_name}."
        ),
        user=user,
    )

    from auditlogs.services import AuditLogService

    AuditLogService.log(
        company=company,
        user=user,
        module='Admissions',
        action='create',
        object_id=student.id,
        description=(
            f"Lead {lead.first_name} {lead.last_name} "
            f"converted to student {student.student_id}."
        ),
    )

    return student
