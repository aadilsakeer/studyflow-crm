from django.core.signing import BadSignature, SignatureExpired, TimestampSigner
from django.utils import timezone

from .models import ClientPortalAccess
from .services import ClientPortalAuthService

PORTAL_TOKEN_SALT = 'student-portal-v1'
PORTAL_TOKEN_MAX_AGE = 60 * 60 * 12


class PortalTokenService:

    @staticmethod
    def create_token(portal_access):
        signer = TimestampSigner(salt=PORTAL_TOKEN_SALT)
        return signer.sign(str(portal_access.id))

    @staticmethod
    def resolve_portal(token):
        if not token:
            return None

        signer = TimestampSigner(salt=PORTAL_TOKEN_SALT)

        try:
            portal_id = signer.unsign(
                token,
                max_age=PORTAL_TOKEN_MAX_AGE,
            )
        except (BadSignature, SignatureExpired):
            return None

        return ClientPortalAccess.objects.select_related(
            'student',
            'student__lead',
            'student__company',
        ).filter(
            pk=portal_id,
            is_active=True,
            student__is_deleted=False,
        ).first()


def authenticate_portal(username, password):
    portal = ClientPortalAccess.objects.select_related(
        'student',
        'student__lead',
        'student__company',
    ).filter(
        username=username,
        is_active=True,
        student__is_deleted=False,
    ).first()

    if not portal:
        return None

    if not ClientPortalAuthService.verify_password(
        password,
        portal.password,
    ):
        return None

    portal.last_login = timezone.now()
    portal.save(update_fields=['last_login'])

    return portal
