from django.db.models import Prefetch, Q

from admissions.models import OfferLetter, Student, VisaCase

from accounts.access import filter_leads_for_user, filter_students_for_user

from .audit_service import log_lead_changes, snapshot_lead
from .journey_constants import (
    JOURNEY_STAGES,
    LEAD_STAGE_STATUSES,
    NEW_LEAD_STATUSES,
    STAGE_LABELS,
    STUDENT_JOURNEY_STAGES,
    VISA_PROCESSING_STATUSES,
)
from .models import Lead, LeadTimeline


def resolve_lead_stage(lead):
    if lead.status in NEW_LEAD_STATUSES:
        return 'new_lead'

    if lead.status in LEAD_STAGE_STATUSES:
        return lead.status

    if lead.status == 'converted':
        return None

    return 'new_lead'


def resolve_student_stage(student, offers=None, visas=None):
    if student.journey_stage in STUDENT_JOURNEY_STAGES:
        return student.journey_stage

    offers = offers if offers is not None else list(
        student.offer_letters.filter(is_deleted=False),
    )
    visas = visas if visas is not None else list(
        student.visa_cases.filter(is_deleted=False),
    )

    if any(v.status == 'approved' for v in visas):
        return 'visa_approved'

    if any(v.status in VISA_PROCESSING_STATUSES for v in visas):
        return 'visa_processing'

    if student.status == 'visa_approved':
        return 'visa_approved'

    if student.status == 'visa_processing':
        return 'visa_processing'

    if any(o.status == 'accepted' for o in offers):
        return 'offer_accepted'

    if any(o.status in ('received', 'reviewed') for o in offers):
        return 'offer_received'

    if student.status == 'offer_received':
        return 'offer_received'

    lead = getattr(student, 'lead', None)

    if lead and lead.status in LEAD_STAGE_STATUSES:
        return lead.status

    if lead and lead.status == 'application_ready':
        return 'application_ready'

    return 'application_ready'


def _card_from_lead(lead):
    university = ''

    if lead.recommended_universities:
        first = lead.recommended_universities[0]
        university = first.get('name', first) if isinstance(first, dict) else str(first)

    return {
        'id': lead.id,
        'entity_type': 'lead',
        'name': f'{lead.first_name} {lead.last_name}'.strip(),
        'phone': lead.phone,
        'stage': resolve_lead_stage(lead),
        'country': lead.country_interest or '',
        'university': university,
        'telecaller_id': lead.assigned_to_id,
        'telecaller_name': _user_name(lead.assigned_to),
        'counsellor_id': lead.assigned_counsellor_id,
        'counsellor_name': _user_name(lead.assigned_counsellor),
    }


def _card_from_student(student):
    offers = list(student.offer_letters.all())
    visas = list(student.visa_cases.all())
    university = ''

    if offers:
        university = offers[0].university

    lead = getattr(student, 'lead', None)

    return {
        'id': student.id,
        'entity_type': 'student',
        'name': student.student_id,
        'phone': lead.phone if lead else '',
        'stage': resolve_student_stage(student, offers, visas),
        'country': student.destination_country or '',
        'university': university,
        'telecaller_id': lead.assigned_to_id if lead else None,
        'telecaller_name': _user_name(
            lead.assigned_to if lead else None,
        ),
        'counsellor_id': student.assigned_counselor_id,
        'counsellor_name': _user_name(student.assigned_counselor),
    }


def _user_name(user):
    if not user:
        return None

    return user.get_full_name() or user.username


JOURNEY_BOARD_MAX_CARDS = 250


def get_journey_board(company, user, filters=None):
    filters = filters or {}

    lead_qs = Lead.objects.filter(
        company=company,
        is_deleted=False,
    ).exclude(
        status='converted',
    ).select_related(
        'assigned_to',
        'assigned_counsellor',
    )

    lead_qs = filter_leads_for_user(lead_qs, user)

    student_qs = Student.objects.filter(
        company=company,
        is_deleted=False,
    ).select_related(
        'lead',
        'lead__assigned_to',
        'assigned_counselor',
    ).prefetch_related(
        Prefetch(
            'offer_letters',
            queryset=OfferLetter.objects.filter(is_deleted=False),
        ),
        Prefetch(
            'visa_cases',
            queryset=VisaCase.objects.filter(is_deleted=False),
        ),
    )

    student_qs = filter_students_for_user(student_qs, user)

    if filters.get('telecaller'):
        lead_qs = lead_qs.filter(
            assigned_to_id=filters['telecaller'],
        )
        student_qs = student_qs.filter(
            lead__assigned_to_id=filters['telecaller'],
        )

    if filters.get('counsellor'):
        lead_qs = lead_qs.filter(
            assigned_counsellor_id=filters['counsellor'],
        )
        student_qs = student_qs.filter(
            assigned_counselor_id=filters['counsellor'],
        )

    if filters.get('country'):
        lead_qs = lead_qs.filter(
            country_interest__icontains=filters['country'],
        )
        student_qs = student_qs.filter(
            destination_country__icontains=filters['country'],
        )

    cards = []

    for lead in lead_qs.iterator():
        cards.append(_card_from_lead(lead))

    for student in student_qs.iterator():
        cards.append(_card_from_student(student))

    if filters.get('university'):
        needle = filters['university'].lower()
        cards = [
            c for c in cards
            if needle in (c.get('university') or '').lower()
        ]

    if filters.get('search'):
        needle = filters['search'].lower()
        cards = [
            c for c in cards
            if needle in c['name'].lower()
            or needle in (c.get('phone') or '').lower()
        ]

    truncated = len(cards) > JOURNEY_BOARD_MAX_CARDS
    if truncated:
        cards = cards[:JOURNEY_BOARD_MAX_CARDS]

    columns = {stage: [] for stage in JOURNEY_STAGES}
    counts = {stage: 0 for stage in JOURNEY_STAGES}

    for card in cards:
        stage = card.get('stage')

        if stage not in columns:
            continue

        columns[stage].append(card)
        counts[stage] += 1

    return {
        'stages': [
            {
                'key': stage,
                'label': STAGE_LABELS[stage],
                'count': counts[stage],
                'cards': columns[stage],
            }
            for stage in JOURNEY_STAGES
        ],
        'total': len(cards),
        'truncated': truncated,
        'max_cards': JOURNEY_BOARD_MAX_CARDS,
    }


def move_to_stage(entity_type, entity_id, stage, company, user):
    if stage not in JOURNEY_STAGES:
        raise ValueError('Invalid stage.')

    if entity_type == 'lead':
        lead = Lead.objects.filter(
            company=company,
            is_deleted=False,
        ).exclude(status='converted').get(pk=entity_id)

        if stage not in LEAD_STAGE_STATUSES and stage != 'new_lead':
            raise ValueError('Stage not valid for lead.')

        old_snapshot = snapshot_lead(lead)
        lead.status = LEAD_STAGE_STATUSES.get(stage, 'new')
        lead.save(update_fields=['status', 'updated_at'])
        log_lead_changes(lead, old_snapshot, user)

        LeadTimeline.objects.create(
            lead=lead,
            action='Journey Stage Moved',
            description=f'Moved to {STAGE_LABELS[stage]}.',
            performed_by=user,
        )

        return _card_from_lead(lead)

    if entity_type == 'student':
        student = Student.objects.filter(
            company=company,
            is_deleted=False,
        ).select_related('lead').get(pk=entity_id)

        if stage in STUDENT_JOURNEY_STAGES:
            student.journey_stage = stage
            student.save(update_fields=['journey_stage'])
        elif stage == 'visa_approved':
            student.status = 'visa_approved'
            student.journey_stage = ''
            student.save(update_fields=['status', 'journey_stage'])
        elif stage == 'visa_processing':
            student.status = 'visa_processing'
            student.journey_stage = ''
            student.save(update_fields=['status', 'journey_stage'])
        elif stage == 'offer_accepted':
            student.status = 'offer_received'
            student.journey_stage = ''
            student.save(update_fields=['status', 'journey_stage'])
            OfferLetter.objects.filter(
                student=student,
                is_deleted=False,
                status='reviewed',
            ).update(status='accepted')
        elif stage == 'offer_received':
            student.status = 'offer_received'
            student.journey_stage = ''
            student.save(update_fields=['status', 'journey_stage'])
        elif stage in LEAD_STAGE_STATUSES:
            student.journey_stage = ''
            student.status = 'counselling'
            student.save(update_fields=['status', 'journey_stage'])

            if hasattr(student, 'lead') and student.lead:
                old_snapshot = snapshot_lead(student.lead)
                student.lead.status = LEAD_STAGE_STATUSES.get(
                    stage,
                    'new',
                )
                student.lead.save(update_fields=['status', 'updated_at'])
                log_lead_changes(student.lead, old_snapshot, user)
        else:
            raise ValueError('Stage not valid for student.')

        student = Student.objects.filter(pk=student.id).select_related(
            'lead',
            'lead__assigned_to',
            'assigned_counselor',
        ).prefetch_related(
            Prefetch(
                'offer_letters',
                queryset=OfferLetter.objects.filter(is_deleted=False),
            ),
            Prefetch(
                'visa_cases',
                queryset=VisaCase.objects.filter(is_deleted=False),
            ),
        ).first()

        return _card_from_student(student)

    raise ValueError('Invalid entity type.')
