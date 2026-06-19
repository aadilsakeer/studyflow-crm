import secrets
import string

from django.db import transaction
from django.utils import timezone

from auditlogs.services import AuditLogService

from .models import CustomUser


def generate_temp_password(length=12):
    alphabet = string.ascii_letters + string.digits + '!@#$'
    return ''.join(secrets.choice(alphabet) for _ in range(length))


class UserPasswordService:

    AUDIT_MODULE = 'accounts'

    @classmethod
    def _audit(cls, user, actor, action, description):
        company = user.company
        if not company and actor and actor.company_id:
            company = actor.company
        if not company:
            return
        AuditLogService.log(
            company=company,
            user=actor,
            module=cls.AUDIT_MODULE,
            action=action,
            object_id=user.id,
            description=description,
        )

    @classmethod
    @transaction.atomic
    def reset_password(cls, target, *, actor=None, password=None):
        temp = password or generate_temp_password()
        target.set_password(temp)
        target.save(update_fields=['password'])
        cls._audit(
            target, actor, 'reset_password',
            f'Password reset for {target.username}',
        )
        return temp

    @classmethod
    @transaction.atomic
    def disable_user(cls, target, *, actor=None):
        target.is_active = False
        target.save(update_fields=['is_active'])
        cls._audit(
            target, actor, 'disable_user',
            f'Disabled user {target.username}',
        )
        return target

    @classmethod
    @transaction.atomic
    def unlock_user(cls, target, *, actor=None):
        target.is_active = True
        target.save(update_fields=['is_active'])
        try:
            from security.models import LoginAttempt
            LoginAttempt.objects.filter(
                user=target,
                success=False,
            ).update(is_suspicious=False, failure_reason='unlocked')
        except Exception:
            pass
        cls._audit(
            target, actor, 'unlock_user',
            f'Unlocked user {target.username}',
        )
        return target

    @classmethod
    def can_manage(cls, actor, target):
        if not actor or not actor.is_authenticated:
            return False
        if actor.is_superuser:
            return True
        if not actor.company_id or actor.company_id != target.company_id:
            return False
        from accounts.constants import ROLE_ADMIN
        return getattr(actor.role, 'name', None) == ROLE_ADMIN
