from rest_framework import serializers

from accounts.models import CustomUser
from core.models import Branch


def get_request_company(context):
    request = context.get("request")

    if not request or not request.user.is_authenticated:
        return None

    return getattr(request.user, "company", None)


def validate_lead_in_company(lead, company):
    if not company:
        raise serializers.ValidationError(
            "Your account is not linked to a company."
        )

    if not lead.company_id or lead.company_id != company.id:
        raise serializers.ValidationError(
            "Lead not found in your company."
        )

    return lead


def validate_student_in_company(student, company):
    if not company:
        raise serializers.ValidationError(
            "Your account is not linked to a company."
        )

    if student.company_id != company.id:
        raise serializers.ValidationError(
            "Student not found in your company."
        )

    return student


def validate_application_in_company(application, company):
    validate_student_in_company(
        application.student,
        company,
    )
    return application


def validate_ticket_in_company(ticket, company):
    return validate_student_in_company(
        ticket.student,
        company,
    )


def validate_user_in_company(user, company):
    if not user:
        return user

    if not company:
        raise serializers.ValidationError(
            "Your account is not linked to a company."
        )

    if user.company_id != company.id:
        raise serializers.ValidationError(
            "User not found in your company."
        )

    return user


def validate_branch_in_company(branch, company):
    if not branch:
        return branch

    if not company:
        raise serializers.ValidationError(
            "Your account is not linked to a company."
        )

    if branch.company_id != company.id:
        raise serializers.ValidationError(
            "Branch not found in your company."
        )

    return branch


def validate_payment_in_company(payment, company):
    if not company:
        raise serializers.ValidationError(
            "Your account is not linked to a company."
        )

    if payment.company_id != company.id:
        raise serializers.ValidationError(
            "Payment not found in your company."
        )

    return payment
