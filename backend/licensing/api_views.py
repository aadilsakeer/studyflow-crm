from django.db.models import Count, Sum
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from datetime import timedelta

from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import PERM_BILLING_MANAGE, PERM_BILLING_VIEW, PERM_SETTINGS_MANAGE
from accounts.permissions import IsCompanyMember, permission_required
from core.models import Company

from accounts.models import CustomUser

from .models import BillingInvoice, BillingPayment, CompanySettings, CompanySubscription, SubscriptionPlan, TenantSupportTicket
from .razorpay_service import RazorpayBillingService
from .serializers import (
    BillingInvoiceSerializer,
    BillingPaymentSerializer,
    CheckoutSerializer,
    CompanySettingsSerializer,
    CompanySubscriptionSerializer,
    OnboardingRegisterSerializer,
    SubscriptionPlanSerializer,
)
from .stripe_service import StripeBillingService
from .subscription_service import OnboardingService, SubscriptionService
from .usage_service import UsageLimitService


class OnboardingRegisterAPIView(APIView):
    permission_classes = []

    def post(self, request):
        serializer = OnboardingRegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        if Company.objects.filter(email=data['admin_email']).exists():
            raise ValidationError({'admin_email': 'Email already registered.'})

        company, user = OnboardingService.register_tenant(
            company_name=data['company_name'],
            admin_email=data['admin_email'],
            admin_password=data['admin_password'],
            admin_first_name=data.get('admin_first_name', ''),
            admin_last_name=data.get('admin_last_name', ''),
            plan_code=data.get('plan_code') or None,
        )

        return Response({
            'company_id': company.id,
            'company_name': company.name,
            'admin_id': user.id,
            'message': 'Trial started successfully.',
        }, status=201)


class CompanySubscriptionAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_VIEW),
    ]

    def get(self, request):
        company = request.user.company
        subscription = UsageLimitService.get_subscription(company)

        if not subscription:
            return Response({'detail': 'No subscription found.'}, status=404)

        return Response(
            CompanySubscriptionSerializer(subscription).data,
        )


class CompanyUsageAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_VIEW),
    ]

    def get(self, request):
        return Response(
            UsageLimitService.get_limits_snapshot(request.user.company),
        )


class CompanySettingsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyMember]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [IsAuthenticated(), IsCompanyMember()]
        return [
            IsAuthenticated(),
            IsCompanyMember(),
            permission_required(PERM_SETTINGS_MANAGE)(),
        ]

    def get(self, request):
        settings, _ = CompanySettings.objects.get_or_create(
            company=request.user.company,
        )
        return Response(
            CompanySettingsSerializer(
                settings,
                context={'request': request},
            ).data,
        )

    def patch(self, request):
        settings, _ = CompanySettings.objects.get_or_create(
            company=request.user.company,
        )
        serializer = CompanySettingsSerializer(
            settings,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            CompanySettingsSerializer(
                settings,
                context={'request': request},
            ).data,
        )


class OnboardingStepAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyMember]

    def post(self, request):
        step = int(request.data.get('step', 1))
        settings = OnboardingService.advance_onboarding(
            request.user.company,
            step,
        )
        return Response(
            CompanySettingsSerializer(
                settings,
                context={'request': request},
            ).data,
        )


class PlanListAPIView(APIView):
    permission_classes = []

    def get(self, request):
        plans = SubscriptionPlan.objects.filter(is_active=True)
        return Response(
            SubscriptionPlanSerializer(plans, many=True).data,
        )


class BillingCheckoutAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_MANAGE),
    ]

    def post(self, request):
        serializer = CheckoutSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        provider = serializer.validated_data['provider']
        billing_cycle = serializer.validated_data['billing_cycle']
        company = request.user.company

        if provider == 'stripe':
            url = StripeBillingService.create_checkout_session(
                company,
                request.user,
                billing_cycle,
            )
            return Response({'checkout_url': url, 'provider': 'stripe'})

        data = RazorpayBillingService.create_subscription(
            company,
            request.user,
            billing_cycle,
        )
        return Response({'provider': 'razorpay', **data})


class BillingPortalAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_MANAGE),
    ]

    def post(self, request):
        url = StripeBillingService.create_portal_session(
            request.user.company,
        )
        return Response({'portal_url': url})


class BillingInvoiceListAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_VIEW),
    ]

    def get(self, request):
        invoices = BillingInvoice.objects.filter(
            company=request.user.company,
        )[:50]
        return Response(
            BillingInvoiceSerializer(invoices, many=True).data,
        )


class BillingPaymentListAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_VIEW),
    ]

    def get(self, request):
        payments = BillingPayment.objects.filter(
            company=request.user.company,
        )[:50]
        return Response(
            BillingPaymentSerializer(payments, many=True).data,
        )


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookAPIView(APIView):
    permission_classes = []

    def post(self, request):
        result = StripeBillingService.handle_webhook(
            request.body,
            request.META.get('HTTP_STRIPE_SIGNATURE', ''),
        )
        return Response(result)


@method_decorator(csrf_exempt, name='dispatch')
class RazorpayWebhookAPIView(APIView):
    permission_classes = []

    def post(self, request):
        sig = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
        result = RazorpayBillingService.handle_webhook(
            request.data, raw_body=request.body, signature=sig,
        )
        if isinstance(result, tuple):
            return Response(result[0], status=result[1])
        return Response(result)


class SaasAdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        companies = Company.objects.order_by('-created_at')[:100]
        expiring_cutoff = timezone.now() + timedelta(days=7)

        rows = []
        for company in companies:
            sub = UsageLimitService.get_subscription(company)
            rows.append({
                'id': company.id,
                'name': company.name,
                'email': company.email,
                'is_active': company.is_active,
                'users': CustomUser.objects.filter(company=company).count(),
                'plan': sub.plan.name if sub else None,
                'status': sub.status if sub else None,
                'trial_ends_at': sub.trial_ends_at if sub else None,
                'current_period_end': sub.current_period_end if sub else None,
                'expiring_soon': bool(
                    sub
                    and sub.current_period_end
                    and sub.current_period_end <= expiring_cutoff
                    and sub.status in ('active', 'trial'),
                ),
            })

        revenue = BillingInvoice.objects.filter(
            status='paid',
        ).aggregate(total=Sum('amount'))['total'] or 0

        open_tickets = TenantSupportTicket.objects.exclude(
            status__in=('resolved', 'closed'),
        ).count()
        sla_breached = TenantSupportTicket.objects.filter(
            sla_status='breached',
        ).exclude(status__in=('resolved', 'closed')).count()
        thirty_days_ago = timezone.now() - timedelta(days=30)
        churned = CompanySubscription.objects.filter(
            status='cancelled',
            cancelled_at__gte=thirty_days_ago,
        ).count()
        new_tenants = Company.objects.filter(
            created_at__gte=thirty_days_ago,
        ).count()
        plan_dist = list(
            CompanySubscription.objects.values('plan__name').annotate(
                count=Count('id'),
            ).order_by('-count'),
        )
        ticket_stats = list(
            TenantSupportTicket.objects.values('status').annotate(
                count=Count('id'),
            ),
        )

        return Response({
            'companies': rows,
            'totals': {
                'companies': Company.objects.count(),
                'active_subscriptions': CompanySubscription.objects.filter(
                    status='active',
                ).count(),
                'trials': CompanySubscription.objects.filter(
                    status='trial',
                ).count(),
                'expiring_soon': CompanySubscription.objects.filter(
                    status__in=('active', 'trial'),
                    current_period_end__lte=expiring_cutoff,
                ).count(),
                'paid_invoices': BillingInvoice.objects.filter(
                    status='paid',
                ).count(),
                'revenue': revenue,
                'open_support_tickets': open_tickets,
                'sla_breached': sla_breached,
                'churn_30d': churned,
                'new_tenants_30d': new_tenants,
            },
            'plan_distribution': plan_dist,
            'ticket_analytics': ticket_stats,
            'health': __import__('core.health', fromlist=['health_snapshot']).health_snapshot(),
        })
