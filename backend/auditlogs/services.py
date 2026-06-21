from .models import AuditLog


class AuditLogService:

    @staticmethod
    def log(
        company,
        user,
        module,
        action,
        object_id,
        description
    ):

        return AuditLog.objects.create(
            company=company,
            user=user,
            module=module,
            action=action,
            object_id=object_id,
            description=description,
        )