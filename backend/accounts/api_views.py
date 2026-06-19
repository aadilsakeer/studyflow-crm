from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_SETTINGS_MANAGE
from accounts.models import CustomUser
from accounts.password_service import UserPasswordService
from accounts.permissions import IsCompanyMember, permission_required
from accounts.serializers import CurrentUserSerializer, StaffUserActionSerializer


class CurrentUserAPIView(APIView):

    def get(self, request):
        serializer = CurrentUserSerializer(
            request.user,
        )
        return Response(serializer.data)


class StaffUserManagementAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_SETTINGS_MANAGE),
    ]

    def post(self, request, user_id):
        target = CustomUser.objects.filter(
            pk=user_id,
            company_id=request.user.company_id,
        ).exclude(pk=request.user.pk).first()
        if not target:
            raise NotFound('User not found.')
        if not UserPasswordService.can_manage(request.user, target):
            raise PermissionDenied()

        ser = StaffUserActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action = ser.validated_data['action']

        if action == 'reset_password':
            temp = UserPasswordService.reset_password(target, actor=request.user)
            return Response({
                'user_id': target.id,
                'username': target.username,
                'temporary_password': temp,
            })
        if action == 'disable':
            UserPasswordService.disable_user(target, actor=request.user)
            return Response({
                'user_id': target.id,
                'username': target.username,
                'is_active': False,
            })
        raise ValidationError({'action': 'Invalid action.'})
