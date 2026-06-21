from django.utils import timezone

from rest_framework.exceptions import ValidationError

from accounts.constants import ROLE_COUNSELLOR
from accounts.models import CustomUser

from activity.timeline_constants import EVENT_COUNSELLOR_ASSIGNED
from activity.timeline_service import record_lead_event

from auditlogs.services import AuditLogService

from .audit_service import log_lead_changes, snapshot_lead
from .models import Lead, LeadTimeline

PIPELINE_TRANSITIONS = {
    'interested': 'qualified',
    'documents_received': 'qualified',
    'follow_up': 'qualified',
    'qualified': 'counsellor_assigned',
    'counsellor_assigned': 'profile_evaluation',
    'profile_evaluation': 'university_selection',
    'university_selection': 'application_ready',
    'application_ready': 'converted',
}

DEFAULT_READINESS = {
    'passport': False,
    'transcripts': False,
    'language_test': False,
    'sop': False,
    'lor': False,
    'financial_docs': False,
}


def get_company_counsellors(company):
    return CustomUser.objects.filter(
        company=company,
        is_active=True,
        role__name=ROLE_COUNSELLOR,
    ).select_related('role')


def validate_counsellor(counsellor, company):
    if not counsellor:
        raise ValidationError(
            {'counsellor_id': 'Counsellor is required.'},
        )

    if counsellor.company_id != company.id:
        raise ValidationError(
            {'counsellor_id': 'Counsellor not in your company.'},
        )

    role = getattr(counsellor, 'role', None)

    if not role or role.name != ROLE_COUNSELLOR:
        raise ValidationError(
            {'counsellor_id': 'Selected user is not a counsellor.'},
        )

    return counsellor


def qualify_lead(lead, user):
    if lead.status in (
        'qualified',
        'counsellor_assigned',
        'profile_evaluation',
        'university_selection',
        'application_ready',
        'converted',
        'not_interested',
    ):
        raise ValidationError(
            {'detail': 'Lead cannot be qualified in current status.'},
        )

    old_snapshot = snapshot_lead(lead)
    lead.status = 'qualified'
    lead.qualified_at = timezone.now()
    lead.qualified_by = user
    lead.save()

    log_lead_changes(lead, old_snapshot, user)

    LeadTimeline.objects.create(
        lead=lead,
        action='Lead Qualified',
        description='Lead marked as qualified for counselling.',
        performed_by=user,
    )

    AuditLogService.log(
        company=lead.company,
        user=user,
        module='Leads',
        action='qualify',
        object_id=lead.id,
        description=f'Qualified lead {lead.phone}',
    )

    return lead


def assign_counsellor(lead, counsellor, user):
    validate_counsellor(counsellor, lead.company)

    old_snapshot = snapshot_lead(lead)

    if lead.status == 'qualified':
        lead.status = 'counsellor_assigned'

    lead.assigned_counsellor = counsellor
    lead.counsellor_assigned_at = timezone.now()
    lead.save()

    log_lead_changes(lead, old_snapshot, user)

    record_lead_event(
        lead,
        EVENT_COUNSELLOR_ASSIGNED,
        description=(
            f'Assigned to '
            f'{counsellor.get_full_name() or counsellor.username}.'
        ),
        user=user,
    )

    AuditLogService.log(
        company=lead.company,
        user=user,
        module='Leads',
        action='assign_counsellor',
        object_id=lead.id,
        description=(
            f'Assigned counsellor to lead {lead.phone}'
        ),
    )

    return lead


def advance_pipeline(lead, user):
    next_status = PIPELINE_TRANSITIONS.get(lead.status)

    if not next_status or next_status == 'converted':
        raise ValidationError(
            {'detail': 'Lead cannot be advanced further.'},
        )

    if lead.status == 'application_ready':
        raise ValidationError(
            {'detail': 'Use convert endpoint to create student.'},
        )

    old_snapshot = snapshot_lead(lead)
    lead.status = next_status
    lead.save()

    log_lead_changes(lead, old_snapshot, user)

    LeadTimeline.objects.create(
        lead=lead,
        action='Pipeline Advanced',
        description=f'Status moved to {next_status}.',
        performed_by=user,
    )

    return lead


def update_pipeline_data(lead, user, data):
    old_snapshot = snapshot_lead(lead)
    allowed = (
        'profile_evaluation_notes',
        'recommended_countries',
        'recommended_universities',
        'application_readiness',
        'country_interest',
    )

    for field in allowed:
        if field in data:
            setattr(lead, field, data[field])

    if not lead.application_readiness:
        lead.application_readiness = DEFAULT_READINESS.copy()

    lead.save()

    log_lead_changes(lead, old_snapshot, user)

    return lead
