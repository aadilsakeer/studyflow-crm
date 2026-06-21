from django.utils import timezone
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.constants import (
    PERM_BILLING_MANAGE,
    PERM_BILLING_VIEW,
    PERM_SETTINGS_MANAGE,
    PERM_SUPPORT_ADD,
    PERM_SUPPORT_MANAGE,
    PERM_SUPPORT_VIEW,
)
from accounts.permissions import IsCompanyMember, permission_required

from .models import TenantSupportTicket
from .serializers import (
    ChangePlanSerializer,
    CompanySettingsSerializer,
    TenantSupportAttachmentSerializer,
    TenantSupportMessageCreateSerializer,
    TenantSupportMessageSerializer,
    TenantSupportTicketCreateSerializer,
    TenantSupportTicketDetailSerializer,
    TenantSupportTicketSerializer,
    TenantSupportTicketUpdateSerializer,
)
from .subscription_service import SubscriptionService
from .support_service import SupportDeskService


class BillingPermissionMixin:
    def get_permissions(self):
        if self.request.method in ('GET', 'HEAD', 'OPTIONS'):
            return [
                IsAuthenticated(),
                IsCompanyMember(),
                permission_required(PERM_BILLING_VIEW)(),
            ]
        return [
            IsAuthenticated(),
            IsCompanyMember(),
            permission_required(PERM_BILLING_MANAGE)(),
        ]


class SupportTicketListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyMember]

    def get_permissions(self):
        if self.request.method == 'POST':
            return [
                IsAuthenticated(),
                IsCompanyMember(),
                permission_required(PERM_SUPPORT_ADD)(),
            ]
        return [
            IsAuthenticated(),
            IsCompanyMember(),
            permission_required(PERM_SUPPORT_VIEW)(),
        ]

    def get(self, request):
        tickets = TenantSupportTicket.objects.filter(
            company=request.user.company,
        )
        for ticket in tickets:
            SupportDeskService.refresh_sla(ticket)
        return Response(
            TenantSupportTicketSerializer(tickets, many=True).data,
        )

    def post(self, request):
        serializer = TenantSupportTicketCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        ticket = SupportDeskService.create_ticket(
            company=request.user.company,
            user=request.user,
            **serializer.validated_data,
        )
        return Response(
            TenantSupportTicketDetailSerializer(
                ticket,
                context={'request': request},
            ).data,
            status=201,
        )


class SupportTicketDetailAPIView(APIView):
    permission_classes = [IsAuthenticated, IsCompanyMember]

    def get_permissions(self):
        if self.request.method == 'GET':
            return [
                IsAuthenticated(),
                IsCompanyMember(),
                permission_required(PERM_SUPPORT_VIEW)(),
            ]
        return [
            IsAuthenticated(),
            IsCompanyMember(),
            permission_required(PERM_SUPPORT_MANAGE)(),
        ]

    def _get_ticket(self, request, pk):
        if request.user.is_superuser:
            ticket = TenantSupportTicket.objects.filter(pk=pk).first()
        else:
            ticket = TenantSupportTicket.objects.filter(
                pk=pk,
                company=request.user.company,
            ).first()
        if not ticket:
            raise NotFound('Ticket not found.')
        SupportDeskService.refresh_sla(ticket)
        return ticket

    def get(self, request, pk):
        ticket = self._get_ticket(request, pk)
        return Response(
            TenantSupportTicketDetailSerializer(
                ticket,
                context={'request': request},
            ).data,
        )

    def patch(self, request, pk):
        ticket = self._get_ticket(request, pk)
        serializer = TenantSupportTicketUpdateSerializer(
            ticket,
            data=request.data,
            partial=True,
        )
        serializer.is_valid(raise_exception=True)
        ticket = serializer.save()

        if ticket.status in (
            TenantSupportTicket.STATUS_RESOLVED,
            TenantSupportTicket.STATUS_CLOSED,
        ) and not ticket.resolved_at:
            ticket.resolved_at = timezone.now()
            ticket.save(update_fields=['resolved_at', 'updated_at'])

        return Response(
            TenantSupportTicketDetailSerializer(
                ticket,
                context={'request': request},
            ).data,
        )


class SupportTicketMessageAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_SUPPORT_VIEW),
    ]

    def post(self, request, pk):
        if request.user.is_superuser:
            ticket = TenantSupportTicket.objects.filter(pk=pk).first()
        else:
            ticket = TenantSupportTicket.objects.filter(
                pk=pk,
                company=request.user.company,
            ).first()

        if not ticket:
            raise NotFound('Ticket not found.')

        serializer = TenantSupportMessageCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        message = SupportDeskService.add_message(
            ticket=ticket,
            user=request.user,
            **serializer.validated_data,
        )
        return Response(
            TenantSupportMessageSerializer(message).data,
            status=201,
        )


class SupportTicketAttachmentAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_SUPPORT_ADD),
    ]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request, pk):
        ticket = TenantSupportTicket.objects.filter(
            pk=pk,
            company=request.user.company,
        ).first()

        if not ticket:
            raise NotFound('Ticket not found.')

        uploaded = request.FILES.get('file')
        if not uploaded:
            raise ValidationError({'file': 'File is required.'})

        attachment = SupportDeskService.add_attachment(
            ticket=ticket,
            user=request.user,
            uploaded_file=uploaded,
        )
        return Response(
            TenantSupportAttachmentSerializer(
                attachment,
                context={'request': request},
            ).data,
            status=201,
        )


class AdminSupportTicketListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get(self, request):
        tickets = TenantSupportTicket.objects.select_related(
            'company',
            'created_by',
        ).order_by('-created_at')[:200]

        rows = []
        for ticket in tickets:
            SupportDeskService.refresh_sla(ticket)
            rows.append({
                'id': ticket.id,
                'company_id': ticket.company_id,
                'company_name': ticket.company.name,
                'subject': ticket.subject,
                'status': ticket.status,
                'priority': ticket.priority,
                'sla_status': ticket.sla_status,
                'sla_due_at': ticket.sla_due_at,
                'created_at': ticket.created_at,
            })

        return Response(rows)


class ChangePlanAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_BILLING_MANAGE),
    ]

    def post(self, request):
        serializer = ChangePlanSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            subscription = SubscriptionService.change_plan(
                request.user.company,
                serializer.validated_data['plan_code'],
            )
        except ValueError as exc:
            raise ValidationError({'detail': str(exc)})

        from .serializers import CompanySubscriptionSerializer

        return Response(CompanySubscriptionSerializer(subscription).data)


class BrandingUploadAPIView(APIView):
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_SETTINGS_MANAGE),
    ]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def post(self, request):
        from .models import CompanySettings

        settings_obj, _ = CompanySettings.objects.get_or_create(
            company=request.user.company,
        )

        if 'brand_logo' in request.FILES:
            settings_obj.brand_logo = request.FILES['brand_logo']
        if 'brand_favicon' in request.FILES:
            settings_obj.brand_favicon = request.FILES['brand_favicon']

        for field in ('brand_name', 'brand_primary_color', 'billing_email'):
            if field in request.data:
                setattr(settings_obj, field, request.data[field])

        settings_obj.save()
        return Response(
            CompanySettingsSerializer(
                settings_obj,
                context={'request': request},
            ).data,
        )
