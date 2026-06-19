from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_BILLING_VIEW
from accounts.permissions import IsCompanyMember, permission_required

from .module_service import ModuleLicensingService
from .serializers import (
    BulkModuleAssignSerializer,
    CompanyModuleActionSerializer,
)


class CompanyModulesAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_VIEW),
    ]

    def get(self, request):
        company = request.user.company
        return Response({
            'active': ModuleLicensingService.active_modules(company),
            'all': ModuleLicensingService.company_modules(company),
        })


class OwnerModuleCatalogAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        return Response(ModuleLicensingService.catalog())


class OwnerCompanyModulesAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, company_id):
        from core.models import Company
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            raise NotFound()
        return Response(ModuleLicensingService.company_modules(company))

    def post(self, request, company_id):
        from core.models import Company
        company = Company.objects.filter(pk=company_id).first()
        if not company:
            raise NotFound()

        ser = CompanyModuleActionSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        action = data['action']
        code = data['module_code']

        try:
            if action == 'enable':
                result = ModuleLicensingService.enable_module(
                    company, code, actor=request.user,
                    expires_at=data.get('expires_at'),
                    usage_limits=data.get('usage_limits'),
                )
            elif action == 'disable':
                result = ModuleLicensingService.disable_module(
                    company, code, actor=request.user,
                )
            elif action == 'trial':
                result = ModuleLicensingService.start_trial(
                    company, code, actor=request.user,
                    days=data.get('trial_days', 14),
                )
            elif action == 'set_expiry':
                result = ModuleLicensingService.set_expiry(
                    company, code, data['expires_at'], actor=request.user,
                )
            elif action == 'set_limits':
                result = ModuleLicensingService.set_usage_limits(
                    company, code, data.get('usage_limits', {}), actor=request.user,
                )
            elif action == 'remove':
                result = ModuleLicensingService.remove_module(
                    company, code, actor=request.user,
                )
            else:
                raise ValidationError({'action': 'Invalid action.'})
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)})

        return Response(result)


class OwnerBulkModuleAssignAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request):
        ser = BulkModuleAssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        data = ser.validated_data
        results = ModuleLicensingService.bulk_assign(
            data['company_ids'],
            data['module_codes'],
            actor=request.user,
            action=data.get('action', 'enable'),
            trial_days=data.get('trial_days', 14),
        )
        return Response({'results': results})
