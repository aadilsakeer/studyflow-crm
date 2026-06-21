import csv
import io
import os
from decimal import Decimal, InvalidOperation

import pandas as pd
from django.db import transaction
from django.utils import timezone

from activity.timeline_constants import EVENT_LEAD_IMPORTED
from activity.timeline_service import record_lead_event

from auditlogs.services import AuditLogService

from accounts.models import CustomUser

from .assignment_service import (
    assign_lead,
    get_company_telecallers,
    round_robin_assign_leads,
    validate_telecaller,
)
from .models import Lead, LeadImportLog

BATCH_SIZE = 100
PREVIEW_LIMIT = 20

TARGET_FIELDS = [
    'first_name',
    'last_name',
    'phone',
    'email',
    'country_interest',
    'city',
    'visa_type',
    'budget',
    'remarks',
]

REQUIRED_FIELDS = ('first_name', 'phone')


def _read_dataframe(import_log):
    path = import_log.stored_file.path
    ext = os.path.splitext(import_log.file_name)[1].lower()

    if ext == '.csv':
        return pd.read_csv(path, dtype=str)

    return pd.read_excel(path, dtype=str)


def parse_upload_file(file_obj, file_name):
    ext = os.path.splitext(file_name)[1].lower()

    if ext not in ('.xlsx', '.csv'):
        raise ValueError(
            'Unsupported format. Use XLSX or CSV.',
        )

    if ext == '.csv':
        df = pd.read_csv(file_obj, dtype=str)
    else:
        df = pd.read_excel(file_obj, dtype=str)

    df = df.fillna('')
    columns = [str(c).strip() for c in df.columns.tolist()]
    df.columns = columns

    rows = []

    for _, row in df.head(PREVIEW_LIMIT).iterrows():
        rows.append(
            {col: str(row.get(col, '')).strip() for col in columns},
        )

    return columns, rows, len(df)


def _cell(row, mapping, field):
    source = mapping.get(field)

    if not source:
        return ''

    return str(row.get(source, '')).strip()


def _normalize_phone(value):
    return ''.join(
        ch for ch in str(value) if ch.isdigit() or ch == '+'
    ).strip()


def _parse_budget(value):
    if not value:
        return None

    try:
        return Decimal(str(value).replace(',', ''))
    except (InvalidOperation, ValueError):
        return None


def map_row(row, mapping):
    first_name = _cell(row, mapping, 'first_name')
    last_name = _cell(row, mapping, 'last_name')
    phone = _normalize_phone(_cell(row, mapping, 'phone'))
    email = _cell(row, mapping, 'email').lower() or None

    return {
        'first_name': first_name,
        'last_name': last_name,
        'phone': phone,
        'email': email,
        'country_interest': _cell(row, mapping, 'country_interest'),
        'city': _cell(row, mapping, 'city'),
        'visa_type': _cell(row, mapping, 'visa_type'),
        'budget': _parse_budget(_cell(row, mapping, 'budget')),
        'remarks': _cell(row, mapping, 'remarks'),
    }


def validate_mapped_row(data, row_number):
    errors = []

    if not data['first_name']:
        errors.append('First name is required.')

    if not data['phone']:
        errors.append('Phone is required.')

    if data['email'] and '@' not in data['email']:
        errors.append('Invalid email format.')

    return [
        {'row': row_number, 'error': err}
        for err in errors
    ]


def _load_existing_keys(company, duplicate_rule):
    phones = set(
        Lead.objects.filter(
            company=company,
            is_deleted=False,
        ).values_list('phone', flat=True),
    )

    emails = set()

    if duplicate_rule in ('email', 'phone_email'):
        emails = set(
            Lead.objects.filter(
                company=company,
                is_deleted=False,
            ).exclude(
                email__isnull=True,
            ).exclude(
                email='',
            ).values_list('email', flat=True),
        )

    return phones, emails


def _is_duplicate(data, duplicate_rule, phones, emails, file_phones, file_emails):
    phone = data['phone']
    email = data.get('email')

    if duplicate_rule == 'phone':
        return phone in phones or phone in file_phones

    if duplicate_rule == 'email':
        if not email:
            return False
        return email in emails or email in file_emails

    phone_dup = phone in phones or phone in file_phones

    if email:
        email_dup = email in emails or email in file_emails
        return phone_dup and email_dup

    return phone_dup


def validate_import(import_log):
    df = _read_dataframe(import_log)
    mapping = import_log.column_mapping or {}
    errors = []
    valid_rows = []
    duplicate_rows = []

    phones, emails = _load_existing_keys(
        import_log.company,
        import_log.duplicate_rule,
    )
    file_phones = set()
    file_emails = set()

    for idx, row in df.iterrows():
        row_number = int(idx) + 2
        row_dict = {col: str(row.get(col, '')).strip() for col in df.columns}
        data = map_row(row_dict, mapping)
        row_errors = validate_mapped_row(data, row_number)

        if row_errors:
            errors.extend(row_errors)
            continue

        if _is_duplicate(
            data,
            import_log.duplicate_rule,
            phones,
            emails,
            file_phones,
            file_emails,
        ):
            duplicate_rows.append(row_number)
            continue

        if data['phone']:
            file_phones.add(data['phone'])

        if data.get('email'):
            file_emails.add(data['email'])

        valid_rows.append(data)

    import_log.total_records = len(df)
    import_log.error_report = errors
    import_log.status = 'validated'
    import_log.save(
        update_fields=[
            'total_records',
            'error_report',
            'status',
        ],
    )

    return {
        'total_records': len(df),
        'valid_count': len(valid_rows),
        'duplicate_count': len(duplicate_rows),
        'error_count': len(errors),
        'errors': errors[:100],
        'duplicate_rows': duplicate_rows[:100],
        '_valid_rows': valid_rows,
    }


def _pick_even_telecallers(company, count):
    telecallers = list(get_company_telecallers(company))

    if not telecallers:
        return []

    base, remainder = divmod(count, len(telecallers))
    picks = []

    for index, telecaller in enumerate(telecallers):
        slots = base + (1 if index < remainder else 0)
        picks.extend([telecaller] * slots)

    return picks


@transaction.atomic
def execute_import(import_log, user, telecaller=None):
    if import_log.status != 'validated':
        raise ValueError('Import must be validated first.')

    validation = validate_import(import_log)
    valid_rows = validation['_valid_rows']
    assignment_mode = import_log.assignment_mode or 'manual'

    if assignment_mode == 'manual':
        if not telecaller:
            raise ValueError('Telecaller required for manual assignment.')

        validate_telecaller(telecaller, import_log.company)

    telecallers = list(
        get_company_telecallers(import_log.company),
    )

    if assignment_mode in ('round_robin', 'even_distribution') and not telecallers:
        raise ValueError('No telecallers available for assignment.')

    created_leads = []
    imported = 0
    failed = validation['error_count']
    duplicates = validation['duplicate_count']

    for index in range(0, len(valid_rows), BATCH_SIZE):
        batch = valid_rows[index:index + BATCH_SIZE]
        batch_leads = []

        for data in batch:
            batch_leads.append(
                Lead(
                    company=import_log.company,
                    first_name=data['first_name'],
                    last_name=data.get('last_name', ''),
                    phone=data['phone'],
                    email=data.get('email'),
                    country_interest=data.get('country_interest', ''),
                    city=data.get('city', ''),
                    visa_type=data.get('visa_type', ''),
                    budget=data.get('budget'),
                    remarks=data.get('remarks', ''),
                    status='new',
                ),
            )

        Lead.objects.bulk_create(
            batch_leads,
            batch_size=BATCH_SIZE,
        )
        created_leads.extend(batch_leads)

    imported = len(created_leads)

    for lead in created_leads:
        record_lead_event(
            lead,
            EVENT_LEAD_IMPORTED,
            description=(
                f'Imported from {import_log.file_name}.'
            ),
            user=user,
        )

    if assignment_mode == 'manual':
        for lead in created_leads:
            assign_lead(lead, telecaller, user)
    elif assignment_mode == 'even_distribution':
        even_picks = _pick_even_telecallers(
            import_log.company,
            len(created_leads),
        )

        for index, lead in enumerate(created_leads):
            assign_lead(lead, even_picks[index], user)
    elif assignment_mode == 'round_robin':
        round_robin_assign_leads(
            created_leads,
            import_log.company,
            user,
        )

    import_log.imported_records = imported
    import_log.duplicate_records = duplicates
    import_log.failed_records = failed
    import_log.status = 'completed'
    import_log.completed_at = timezone.now()
    import_log.save()

    AuditLogService.log(
        company=import_log.company,
        user=user,
        module='Leads',
        action='import',
        object_id=import_log.id,
        description=(
            f'Imported {imported} leads from '
            f'{import_log.file_name}'
        ),
    )

    return {
        'imported_records': imported,
        'duplicate_records': duplicates,
        'failed_records': failed,
        'total_records': import_log.total_records,
    }
