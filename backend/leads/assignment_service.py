from django.db import transaction
from django.db.models import Count
from django.utils import timezone

from rest_framework.exceptions import ValidationError

from accounts.constants import ROLE_TELECALLER
from accounts.models import CustomUser

from activity.timeline_constants import (
    EVENT_TELECALLER_ASSIGNED,
)
from activity.timeline_service import record_lead_event

from auditlogs.services import AuditLogService

from .audit_service import log_lead_changes, snapshot_lead
from .models import Lead, LeadTimeline

INACTIVE_ASSIGN_STATUSES = (
    'converted',
    'not_interested',
)


def get_company_telecallers(company):
    return CustomUser.objects.filter(
        company=company,
        is_active=True,
        role__name=ROLE_TELECALLER,
    ).select_related('role')


def validate_telecaller(telecaller, company):
    if not telecaller:
        raise ValidationError(
            {'telecaller_id': 'Telecaller is required.'},
        )

    if telecaller.company_id != company.id:
        raise ValidationError(
            {'telecaller_id': 'Telecaller not in your company.'},
        )

    role = getattr(telecaller, 'role', None)

    if not role or role.name != ROLE_TELECALLER:
        raise ValidationError(
            {'telecaller_id': 'Selected user is not a telecaller.'},
        )

    return telecaller


def _telecaller_loads(company, telecallers):
    load_map = {user.id: 0 for user in telecallers}

    rows = Lead.objects.filter(
        company=company,
        is_deleted=False,
        assigned_to__in=telecallers,
    ).exclude(
        status__in=INACTIVE_ASSIGN_STATUSES,
    ).values(
        'assigned_to',
    ).annotate(
        total=Count('id'),
    )

    for row in rows:
        load_map[row['assigned_to']] = row['total']

    return load_map


def pick_least_loaded_telecaller(company, telecallers):
    telecallers = list(telecallers)

    if not telecallers:
        raise ValidationError(
            {'detail': 'No telecallers available in your company.'},
        )

    load_map = _telecaller_loads(company, telecallers)

    return min(
        telecallers,
        key=lambda user: load_map[user.id],
    )


@transaction.atomic
def assign_lead(lead, telecaller, assigned_by):
    old_snapshot = snapshot_lead(lead)
    lead.assigned_to = telecaller
    lead.assigned_at = timezone.now()

    if lead.status == 'new':
        lead.status = 'assigned'

    lead.save()

    log_lead_changes(
        lead,
        old_snapshot,
        assigned_by,
    )

    record_lead_event(
        lead,
        EVENT_TELECALLER_ASSIGNED,
        description=(
            f'Assigned to '
            f'{telecaller.get_full_name() or telecaller.username}.'
        ),
        user=assigned_by,
    )

    AuditLogService.log(
        company=lead.company,
        user=assigned_by,
        module='Leads',
        action='assign',
        object_id=lead.id,
        description=(
            f'Assigned lead {lead.phone} to '
            f'{telecaller.username}'
        ),
    )

    return lead


@transaction.atomic
def assign_leads_to_telecaller(
    leads,
    telecaller,
    assigned_by,
):
    updated = []

    for lead in leads:
        updated.append(
            assign_lead(lead, telecaller, assigned_by),
        )

    return updated


@transaction.atomic
def round_robin_assign_leads(leads, company, assigned_by):
    telecallers = list(get_company_telecallers(company))
    load_map = _telecaller_loads(company, telecallers)
    updated = []

    for lead in leads:
        telecaller = min(
            telecallers,
            key=lambda user: load_map[user.id],
        )
        assign_lead(lead, telecaller, assigned_by)
        load_map[telecaller.id] += 1
        updated.append(lead)

    return updated


def get_assignable_leads(queryset, lead_ids):
    leads = list(
        queryset.filter(
            pk__in=lead_ids,
            is_deleted=False,
        ),
    )

    if len(leads) != len(set(lead_ids)):
        raise ValidationError(
            {'lead_ids': 'One or more leads were not found.'},
        )

    return leads
