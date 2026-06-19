from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser

from .owner_service import OwnerConsoleService
from .platform_service import PlatformOpsService
from .serializers import ChangePlanSerializer, OwnerOnboardSerializer, OwnerUserActionSerializer


class OwnerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(OwnerConsoleService.dashboard())


class OwnerOnboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        ser = OwnerOnboardSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        result = OwnerConsoleService.onboard_tenant(
            name=data['name'],
            email=data.get('email', ''),
            admin_email=data['admin_email'],
            plan_code=data.get('plan_code') or None,
            module_codes=data.get('module_codes') or [],
            admin_first_name=data.get('admin_first_name', ''),
            admin_last_name=data.get('admin_last_name', ''),
            actor=request.user,
        )
        return Response(result, status=201)


class OwnerCompanyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(OwnerConsoleService.list_companies())

    def post(self, request):
        return OwnerOnboardAPIView().post(request)


class OwnerCompanyDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, company_id):
        data = OwnerConsoleService.company_deep_view(company_id)
        if not data:
            raise NotFound()
        return Response(data)

    def patch(self, request, company_id):
        action = request.data.get('action')
        if action == 'activate':
            PlatformOpsService.set_company_active(company_id, True)
        elif action == 'suspend':
            PlatformOpsService.set_company_active(company_id, False)
        elif action == 'change_plan':
            ser = ChangePlanSerializer(data=request.data)
            ser.is_valid(raise_exception=True)
            PlatformOpsService.admin_change_plan(company_id, ser.validated_data['plan_code'])
        elif action == 'extend_trial':
            days = int(request.data.get('days', 7))
            PlatformOpsService.extend_trial(company_id, days=days)
        elif action == 'reset_usage':
            PlatformOpsService.reset_usage(company_id)
        else:
            raise ValidationError({'action': 'Invalid action.'})
        return Response(OwnerConsoleService.company_deep_view(company_id))

    def delete(self, request, company_id):
        OwnerConsoleService.delete_company(company_id)
        return Response(status=204)


class OwnerUserManagementAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        ser = OwnerUserActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        action = ser.validated_data['action']
        if action == 'reset_password':
            result = OwnerConsoleService.reset_user_password(user_id, actor=request.user)
        elif action == 'disable':
            result = OwnerConsoleService.set_user_active(user_id, active=False, actor=request.user)
        elif action == 'unlock':
            result = OwnerConsoleService.set_user_active(user_id, active=True, actor=request.user)
        else:
            raise ValidationError({'action': 'Invalid action.'})
        if not result:
            raise NotFound('User not found.')
        return Response(result)


class OwnerImpersonateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, company_id):
        user_id = request.data.get('user_id')
        if user_id:
            user = CustomUser.objects.filter(pk=user_id, company_id=company_id, is_active=True).first()
        else:
            from accounts.constants import ROLE_ADMIN
            user = CustomUser.objects.filter(
                company_id=company_id, role__name=ROLE_ADMIN, is_active=True,
            ).first()
        if not user:
            raise NotFound('No admin user for this company.')
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'company_id': company_id,
            'company_name': user.company.name if user.company else None,
        })
