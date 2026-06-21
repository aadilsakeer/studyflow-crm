from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_BILLING_MANAGE
from accounts.permissions import IsCompanyMember, permission_required

from .serializers import ChangePlanSerializer, CompanySubscriptionSerializer
from .subscription_service import SubscriptionService


class CancelSubscriptionAPIView(APIView):
    permission_classes = [
        IsAuthenticated, IsCompanyMember, permission_required(PERM_BILLING_MANAGE),
    ]

    def post(self, request):
        sub = SubscriptionService.cancel_subscription(request.user.company)
        return Response(CompanySubscriptionSerializer(sub).data)


class DowngradePlanAPIView(APIView):
    permission_classes = [
        IsAuthenticated, IsCompanyMember, permission_required(PERM_BILLING_MANAGE),
    ]

    def post(self, request):
        serializer = ChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            sub = SubscriptionService.downgrade_plan(
                request.user.company,
                serializer.validated_data['plan_code'],
            )
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response(CompanySubscriptionSerializer(sub).data)


class PublicBrandingAPIView(APIView):
    permission_classes = []

    def get(self, request):
        from .models import CompanySettings
        email = request.query_params.get('email', '')
        defaults = {
            'brand_name': 'Globvio',
            'brand_primary_color': '#2563EB',
            'brand_logo_url': None,
            'brand_favicon_url': None,
        }
        if not email:
            return Response(defaults)
        settings = CompanySettings.objects.filter(
            billing_email=email,
        ).select_related('company').first()
        if not settings:
            return Response(defaults)
        from .serializers import CompanySettingsSerializer
        data = CompanySettingsSerializer(settings, context={'request': request}).data
        return Response({
            'brand_name': data.get('brand_name') or settings.company.name,
            'brand_primary_color': data.get('brand_primary_color'),
            'brand_logo_url': data.get('brand_logo_url'),
            'brand_favicon_url': data.get('brand_favicon_url'),
        })
