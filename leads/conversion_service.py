from django.db import transaction

from rest_framework.exceptions import ValidationError

from admissions.models import Student
from leads.models import Lead, LeadTimeline


def generate_student_id(company):
    count = Student.objects.filter(
        company=company,
    ).count()

    return f"STU-{company.id:03d}-{count + 1:05d}"


@transaction.atomic
def convert_lead_to_student(lead, user):
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

    LeadTimeline.objects.create(
        lead=lead,
        action="Converted to Student",
        description=(
            f"Lead converted to student "
            f"{student.student_id}."
        ),
        performed_by=user,
    )

    return student
