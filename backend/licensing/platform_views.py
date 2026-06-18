from datetime import timedelta

from django.db.models import Count, Sum
from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import CustomUser
from auditlogs.models import AuditLog
from auditlogs.serializers import AuditLogSerializer
from core.models import Company

from .models import (
    BillingInvoice,
    BillingPayment,
    CompanySubscription,
    TenantSupportTicket,
)
from .platform_service import PlatformOpsService
from .serializers import ChangePlanSerializer, TenantSupportTicketUpdateSerializer
from .support_service import SupportDeskService
from .usage_service import UsageLimitService


class PlatformOperationsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        now = timezone.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        expiring_cutoff = now + timedelta(days=7)

        monthly_revenue = BillingInvoice.objects.filter(
            status='paid', paid_at__gte=month_start,
        ).aggregate(t=Sum('amount'))['t'] or 0

        failed_payments = list(BillingPayment.objects.filter(
            status='failed',
        ).order_by('-created_at')[:20].values(
            'id', 'company_id', 'amount', 'provider', 'created_at',
        ))

        expiring = list(CompanySubscription.objects.filter(
            status__in=('active', 'trial'),
            current_period_end__lte=expiring_cutoff,
        ).select_related('company', 'plan').values(
            'company_id', 'company__name', 'plan__name', 'status',
            'current_period_end', 'trial_ends_at',
        )[:20])

        renewals = list(BillingInvoice.objects.filter(
            status='paid', paid_at__gte=month_start,
        ).order_by('-paid_at')[:20].values(
            'invoice_number', 'company_id', 'amount', 'paid_at',
        ))

        active_plans = list(
            CompanySubscription.objects.filter(status='active').values(
                'plan__name',
            ).annotate(count=Count('id')),
        )

        return Response({
            'totals': {
                'companies': Company.objects.count(),
                'active_subscriptions': CompanySubscription.objects.filter(status='active').count(),
                'trials': CompanySubscription.objects.filter(status='trial').count(),
                'monthly_revenue': monthly_revenue,
                'open_support_tickets': TenantSupportTicket.objects.exclude(
                    status__in=('resolved', 'closed'),
                ).count(),
            },
            'active_plans': active_plans,
            'failed_payments': failed_payments,
            'expiring_subscriptions': expiring,
            'renewals': renewals,
        })


class AdminTenantDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, company_id):
        action = request.data.get('action')
        if action == 'activate':
            PlatformOpsService.set_company_active(company_id, True)
        elif action == 'suspend':
            PlatformOpsService.set_company_active(company_id, False)
        else:
            raise ValidationError({'action': 'Use activate or suspend.'})
        company = Company.objects.get(pk=company_id)
        return Response({'id': company.id, 'is_active': company.is_active})


class AdminTenantPlanAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, company_id):
        ser = ChangePlanSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        try:
            sub = PlatformOpsService.admin_change_plan(
                company_id, ser.validated_data['plan_code'],
            )
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)})
        return Response({'plan': sub.plan.name, 'status': sub.status})


class AdminTenantTrialAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, company_id):
        days = int(request.data.get('days', 7))
        sub = PlatformOpsService.extend_trial(company_id, days=days)
        return Response({'trial_ends_at': sub.trial_ends_at})


class AdminTenantResetUsageAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, company_id):
        PlatformOpsService.reset_usage(company_id)
        return Response({'reset': True})


class AdminSupportTicketOpsAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def patch(self, request, pk):
        ticket = TenantSupportTicket.objects.filter(pk=pk).first()
        if not ticket:
            raise NotFound()
        if request.data.get('escalate'):
            ticket.priority = TenantSupportTicket.PRIORITY_URGENT
            ticket.status = TenantSupportTicket.STATUS_IN_PROGRESS
            SupportDeskService.compute_sla(ticket)
            ticket.save()
        ser = TenantSupportTicketUpdateSerializer(ticket, data=request.data, partial=True)
        ser.is_valid(raise_exception=True)
        ticket = ser.save()
        SupportDeskService.refresh_sla(ticket)
        return Response({'id': ticket.id, 'status': ticket.status, 'assigned_to': ticket.assigned_to_id})


class AdminImpersonateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def post(self, request, user_id):
        user = CustomUser.objects.filter(pk=user_id, is_active=True).first()
        if not user:
            raise NotFound('User not found.')
        refresh = RefreshToken.for_user(user)
        return Response({
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user_id': user.id,
            'company_id': user.company_id,
        })


class AdminTenantActivityAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request, company_id):
        logs = AuditLog.objects.filter(company_id=company_id).order_by('-created_at')[:50]
        return Response(AuditLogSerializer(logs, many=True).data)
