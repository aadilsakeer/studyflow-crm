from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser

from .owner_service import OwnerConsoleService
from .platform_service import PlatformOpsService
from .serializers import ChangePlanSerializer


class OwnerDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(OwnerConsoleService.dashboard())


class OwnerCompanyListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(OwnerConsoleService.list_companies())

    def post(self, request):
        data = request.data
        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        admin_email = data.get('admin_email', email).strip()
        password = data.get('admin_password', '')
        if not name or not admin_email or len(password) < 8:
            raise ValidationError('name, admin_email, and admin_password (8+) required.')
        company, user = OwnerConsoleService.create_company(
            name=name, email=email, admin_email=admin_email, admin_password=password,
        )
        return Response({'company_id': company.id, 'admin_id': user.id}, status=201)


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
