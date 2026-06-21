from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.permissions import (
    ActionPermissionMixin,
    crm_permission_map,
)
from core.mixins import require_company
from licensing.decorators import module_required

from .message_service import (
    connect_user_session,
    get_connected_account,
    refresh_session_status,
    send_whatsapp_message,
)
from .models import WhatsAppAccount
from .openwa_client import (
    OpenWAError,
    enrich_openwa_error,
    fetch_session_qr,
    get_client_for_company,
    humanize_openwa_error,
    is_session_missing_error,
)
from .integration_serializers import WhatsAppSendSerializer


class WhatsAppSendAPIView(ActionPermissionMixin, APIView):
    permission_map = crm_permission_map('whatsapp')

    @module_required('whatsapp')
    def post(self, request):
        company = require_company(request.user)
        serializer = WhatsAppSendSerializer(
            data=request.data,
            context={'request': request},
        )
        serializer.is_valid(raise_exception=True)

        lead = serializer.validated_data.get('lead')
        student = serializer.validated_data.get('student')
        message = serializer.validated_data['message']
        phone = serializer.validated_data.get(
            'recipient_number',
        )

        if not phone:
            if student:
                phone = student.lead.phone
            elif lead:
                phone = lead.phone

        if not phone:
            raise ValidationError(
                {
                    'recipient_number': (
                        'Phone number is required.'
                    ),
                },
            )

        try:
            record = send_whatsapp_message(
                company=company,
                user=request.user,
                recipient_number=phone,
                message=message,
                message_type='manual',
                lead=lead,
                student=student,
            )
        except OpenWAError as exc:
            client, _server = get_client_for_company(company)
            account = get_connected_account(company, user=request.user)
            detail = str(exc)

            if client and account and account.session_id:
                detail = enrich_openwa_error(
                    client,
                    account.session_id,
                    exc,
                )

            raise ValidationError(
                {'detail': detail},
            ) from exc

        return Response({
            'id': record.id,
            'status': record.status,
            'recipient_number': record.recipient_number,
            'message': record.message,
            'created_at': record.created_at,
        })


class WhatsAppSessionConnectAPIView(
    ActionPermissionMixin,
    APIView,
):
    permission_map = crm_permission_map('whatsapp')

    @module_required('whatsapp')
    def post(self, request):
        require_company(request.user)
        phone_number = request.data.get(
            'phone_number',
            '',
        )

        try:
            account, qr = connect_user_session(
                request.user,
                phone_number=phone_number,
            )
        except OpenWAError as exc:
            raise ValidationError(
                {'detail': str(exc)},
            ) from exc

        return Response({
            'account_id': account.id,
            'session_id': account.session_id,
            'is_connected': account.is_connected,
            'qr': qr,
        })


class WhatsAppSessionStatusAPIView(
    ActionPermissionMixin,
    APIView,
):
    permission_map = crm_permission_map('whatsapp')

    @module_required('whatsapp')
    def get(self, request):
        company = require_company(request.user)

        account = WhatsAppAccount.objects.filter(
            company=company,
            user=request.user,
        ).first()

        if not account:
            return Response({
                'connected': False,
                'session_id': None,
            })

        account = refresh_session_status(account)

        session_status = None

        try:
            from .openwa_client import get_client_for_company

            client, _server = get_client_for_company(company)

            if (
                client
                and account.session_id
                and not account.session_id.startswith('pending-')
            ):
                session_status = client.get_session(
                    account.session_id,
                ).get('status')
        except OpenWAError:
            pass

        return Response({
            'connected': account.is_connected,
            'session_id': account.session_id,
            'phone_number': account.phone_number,
            'last_connected_at': account.last_connected_at,
            'status': session_status,
        })


class WhatsAppSessionQRAPIView(
    ActionPermissionMixin,
    APIView,
):
    permission_map = crm_permission_map('whatsapp')

    @module_required('whatsapp')
    def get(self, request):
        company = require_company(request.user)

        account = WhatsAppAccount.objects.filter(
            company=company,
            user=request.user,
        ).first()

        if not account or not account.session_id:
            raise ValidationError(
                {'detail': 'No WhatsApp session found.'},
            )

        from .openwa_client import get_client_for_company

        client, _server = get_client_for_company(company)

        if not client:
            raise ValidationError(
                {'detail': 'OpenWA server not configured.'},
            )

        try:
            qr = fetch_session_qr(
                client,
                account.session_id,
            )
        except OpenWAError as exc:
            if is_session_missing_error(exc):
                account, qr = connect_user_session(request.user)
                return Response({
                    'account_id': account.id,
                    'session_id': account.session_id,
                    'is_connected': account.is_connected,
                    'qr': qr,
                    'recovered': True,
                })

            raise ValidationError(
                {
                    'detail': enrich_openwa_error(
                        client,
                        account.session_id,
                        exc,
                    ),
                },
            ) from exc

        return Response({'qr': qr})
