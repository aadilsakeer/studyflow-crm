from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

from .services import record_login_attempt, verify_2fa


class SecureTokenObtainPairSerializer(TokenObtainPairSerializer):
    totp_code = serializers.CharField(required=False, allow_blank=True)
    backup_code = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        username = attrs.get('username', '')
        request = self.context.get('request')
        ip = request.META.get('REMOTE_ADDR', '') if request else ''
        ua = request.META.get('HTTP_USER_AGENT', '') if request else ''

        try:
            data = super().validate(attrs)
        except Exception as exc:
            record_login_attempt(
                username=username, user=None, success=False,
                ip=ip, user_agent=ua, reason=str(exc),
            )
            raise

        user = self.user
        try:
            verify_2fa(
                user,
                code=attrs.get('totp_code') or None,
                backup_code=attrs.get('backup_code') or None,
            )
        except (ValidationError, DjangoValidationError) as exc:
            record_login_attempt(
                username=username, user=user, success=False,
                ip=ip, user_agent=ua, reason='2fa_failed',
            )
            detail = exc.detail[0] if hasattr(exc, 'detail') and exc.detail else str(exc)
            raise ValidationError({'detail': detail})
        record_login_attempt(
            username=username, user=user, success=True,
            ip=ip, user_agent=ua,
        )
        from .services import log_security_event
        log_security_event(user, 'login_success', ip=ip)
        return data


class TwoFAEnableSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=8)


class RevokeSessionsSerializer(serializers.Serializer):
    user_id = serializers.IntegerField(required=False)
