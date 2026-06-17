from leads.models import LeadAuditLog

TRACKED_FIELDS = (
    "first_name",
    "last_name",
    "phone",
    "email",
    "country_interest",
    "city",
    "visa_type",
    "status",
    "remarks",
    "budget",
    "assigned_to",
    "source",
)


def snapshot_lead(lead):
    return {
        field: _field_value(lead, field)
        for field in TRACKED_FIELDS
    }


def _field_value(lead, field):
    value = getattr(lead, field)

    if value is None:
        return ""

    if field in ("assigned_to", "source"):
        return str(value)

    return str(value)


def log_lead_created(lead, user):
    LeadAuditLog.objects.create(
        lead=lead,
        field_changed="created",
        old_value="",
        new_value=(
            f"{lead.first_name} "
            f"{lead.last_name}".strip()
        ),
        changed_by=user,
    )


def log_lead_changes(lead, old_snapshot, user):
    for field in TRACKED_FIELDS:
        old_value = old_snapshot.get(
            field,
            "",
        )
        new_value = _field_value(
            lead,
            field,
        )

        if old_value == new_value:
            continue

        LeadAuditLog.objects.create(
            lead=lead,
            field_changed=field,
            old_value=old_value,
            new_value=new_value,
            changed_by=user,
        )
