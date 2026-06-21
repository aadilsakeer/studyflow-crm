from auditlogs.services import AuditLogService


def log_audit(
    *,
    company,
    user,
    module,
    action,
    object_id,
    description,
):
    if not company or not user:
        return None

    return AuditLogService.log(
        company=company,
        user=user,
        module=module,
        action=action,
        object_id=object_id,
        description=description[:2000],
    )
