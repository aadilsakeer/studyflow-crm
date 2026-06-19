from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView

from accounts.models import CustomUser

from .serializers import RevokeSessionsSerializer, SecureTokenObtainPairSerializer, TwoFAEnableSerializer
from .services import (
    enable_totp,
    get_user_security_events,
    revoke_user_sessions,
    security_dashboard,
    setup_totp,
    validate_password_policy,
)

class SecureTokenObtainPairView(TokenObtainPairView):
    serializer_class = SecureTokenObtainPairSerializer


class TwoFASetupAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        return Response(setup_totp(request.user))


class TwoFAEnableAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = TwoFAEnableSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            return Response(enable_totp(request.user, ser.validated_data['code']))
        except DjangoValidationError as exc:
            raise ValidationError(str(exc.message if hasattr(exc, 'message') else exc))

class SecurityDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser and not request.user.company_id:
            return Response({'detail': 'Forbidden.'}, status=403)
        return Response(security_dashboard(request.user))


class RevokeSessionsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        ser = RevokeSessionsSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        target = request.user
        uid = ser.validated_data.get('user_id')
        if uid:
            if not request.user.is_superuser:
                target = CustomUser.objects.filter(
                    pk=uid, company_id=request.user.company_id,
                ).first()
                if not target:
                    return Response({'detail': 'Forbidden.'}, status=403)
            else:
                target = CustomUser.objects.filter(pk=uid).first()
                if not target:
                    return Response({'detail': 'Not found.'}, status=404)
        count = revoke_user_sessions(target)
        return Response({'revoked': count})


class PasswordPolicyCheckAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        password = request.data.get('password', '')
        try:
            validate_password_policy(password, user=request.user)
            return Response({'valid': True})
        except Exception as exc:
            return Response({'valid': False, 'errors': [str(exc)]})


class UserSecurityEventsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.query_params.get('user_id')
        target = request.user
        if user_id:
            if not request.user.is_superuser:
                target = CustomUser.objects.filter(
                    pk=user_id, company_id=request.user.company_id,
                ).first()
                if not target:
                    return Response({'detail': 'Forbidden.'}, status=403)
            else:
                target = CustomUser.objects.filter(pk=user_id).first()
                if not target:
                    return Response({'detail': 'Not found.'}, status=404)
        return Response({'events': get_user_security_events(request.user, target)})