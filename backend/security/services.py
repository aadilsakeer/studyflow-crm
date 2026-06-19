import secrets
import hashlib

import pyotp
from django.conf import settings
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta

from accounts.models import CustomUser

from .models import LoginAttempt, SecurityEvent, UserSecurityProfile


def validate_password_policy(password, user=None):
    validate_password(password, user=user)
    if len(password) < getattr(settings, 'SECURITY_PASSWORD_MIN_LENGTH', 8):
        raise ValidationError('Password must be at least 8 characters.')
    if not any(c.isupper() for c in password):
        raise ValidationError('Password must include an uppercase letter.')
    if not any(c.islower() for c in password):
        raise ValidationError('Password must include a lowercase letter.')
    if not any(c.isdigit() for c in password):
        raise ValidationError('Password must include a digit.')


def get_or_create_profile(user):
    profile, _ = UserSecurityProfile.objects.get_or_create(user=user)
    return profile


def setup_totp(user):
    profile = get_or_create_profile(user)
    profile.totp_secret = pyotp.random_base32()
    profile.totp_enabled = False
    profile.save(update_fields=['totp_secret', 'totp_enabled'])
    uri = pyotp.totp.TOTP(profile.totp_secret).provisioning_uri(
        name=user.email or user.username,
        issuer_name=getattr(settings, 'SECURITY_TOTP_ISSUER', 'Globvio'),
    )
    return {'secret': profile.totp_secret, 'provisioning_uri': uri}


def enable_totp(user, code):
    profile = get_or_create_profile(user)
    if not profile.totp_secret:
        raise ValidationError('Run 2FA setup first.')
    totp = pyotp.TOTP(profile.totp_secret)
    if not totp.verify(code, valid_window=1):
        raise ValidationError('Invalid verification code.')
    codes = [secrets.token_hex(4) for _ in range(8)]
    profile.totp_enabled = True
    profile.backup_codes = [_hash_code(c) for c in codes]
    profile.save(update_fields=['totp_enabled', 'backup_codes'])
    _log_event(user, '2fa_enabled')
    return {'backup_codes': codes}


def verify_2fa(user, code=None, backup_code=None):
    profile = get_or_create_profile(user)
    if not profile.totp_enabled:
        return True
    if backup_code:
        h = _hash_code(backup_code.strip().lower())
        if h in (profile.backup_codes or []):
            profile.backup_codes = [c for c in profile.backup_codes if c != h]
            profile.save(update_fields=['backup_codes'])
            return True
        raise ValidationError('Invalid backup code.')
    if not code:
        raise ValidationError('2FA code required.')
    if not pyotp.TOTP(profile.totp_secret).verify(code, valid_window=1):
        raise ValidationError('Invalid 2FA code.')
    return True


def _hash_code(code):
    return hashlib.sha256(code.encode()).hexdigest()


def device_fingerprint(ip, user_agent):
    raw = f'{ip}|{user_agent or ""}'[:512]
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def record_login_attempt(*, username, user, success, ip, user_agent, reason=''):
    fp = device_fingerprint(ip, user_agent)
    suspicious = False
    if not success:
        recent_fails = LoginAttempt.objects.filter(
            ip_address=ip,
            success=False,
            created_at__gte=timezone.now() - timedelta(minutes=15),
        ).count()
        if recent_fails >= 4:
            suspicious = True
    elif user:
        prior = LoginAttempt.objects.filter(
            user=user, success=True,
        ).exclude(device_fingerprint=fp).exists()
        had_success = LoginAttempt.objects.filter(user=user, success=True).exists()
        if had_success and prior:
            last_fps = set(
                LoginAttempt.objects.filter(user=user, success=True)
                .order_by('-created_at')[:10]
                .values_list('device_fingerprint', flat=True)
            )
            if fp not in last_fps:
                suspicious = True

    attempt = LoginAttempt.objects.create(
        user=user if success else None,
        username_attempted=username,
        company=user.company if user and success else None,
        ip_address=ip or '',
        user_agent=(user_agent or '')[:500],
        device_fingerprint=fp,
        success=success,
        failure_reason=reason[:255],
        is_suspicious=suspicious,
    )
    if suspicious:
        _log_event(
            user,
            'suspicious_login',
            ip=ip,
            metadata={'username': username, 'attempt_id': attempt.id},
        )
    return attempt


def _log_event(user, event_type, ip='', metadata=None):
    SecurityEvent.objects.create(
        user=user,
        company=user.company if user else None,
        event_type=event_type,
        ip_address=ip or '',
        metadata=metadata or {},
    )


def log_security_event(user, event_type, ip='', metadata=None):
    _log_event(user, event_type, ip=ip, metadata=metadata)


def get_user_security_events(actor, target_user):
    qs = SecurityEvent.objects.filter(user=target_user)
    if not actor.is_superuser:
        if not actor.company_id or target_user.company_id != actor.company_id:
            return []
        qs = qs.filter(company_id=actor.company_id)
    return list(
        qs.order_by('-created_at')[:50].values(
            'event_type', 'ip_address', 'metadata', 'created_at',
        ),
    )


def revoke_user_sessions(user):
    from rest_framework_simplejwt.token_blacklist.models import OutstandingToken

    count = 0
    for token in OutstandingToken.objects.filter(user=user):
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            RefreshToken(token.token).blacklist()
            count += 1
        except Exception:
            pass
    _log_event(user, 'session_revoked', metadata={'count': count})
    return count


def security_dashboard(user):
    qs_attempts = LoginAttempt.objects.all()
    qs_events = SecurityEvent.objects.all()
    if not user.is_superuser:
        if not user.company_id:
            return {}
        qs_attempts = qs_attempts.filter(company_id=user.company_id)
        qs_events = qs_events.filter(company_id=user.company_id)

    since = timezone.now() - timedelta(hours=24)
    profile_qs = UserSecurityProfile.objects.filter(totp_enabled=True)
    if not user.is_superuser and user.company_id:
        profile_qs = profile_qs.filter(user__company_id=user.company_id)
    return {
        'failed_logins_24h': qs_attempts.filter(success=False, created_at__gte=since).count(),
        'successful_logins_24h': qs_attempts.filter(success=True, created_at__gte=since).count(),
        'suspicious_24h': qs_attempts.filter(is_suspicious=True, created_at__gte=since).count(),
        'users_with_2fa': profile_qs.count(),
        'recent_attempts': list(
            qs_attempts.order_by('-created_at')[:20].values(
                'username_attempted', 'ip_address', 'success',
                'is_suspicious', 'created_at', 'failure_reason',
            ),
        ),
        'recent_events': list(
            qs_events.order_by('-created_at')[:20].values(
                'event_type', 'ip_address', 'metadata', 'created_at',
            ),
        ),
    }
