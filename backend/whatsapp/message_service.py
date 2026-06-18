from django.utils import timezone

from .models import WhatsAppAccount, WhatsAppMessage, WhatsAppReminderLog
from .openwa_client import (
    OpenWAError,
    extract_qr_payload,
    extract_session_id,
    get_client_for_company,
    is_session_connected,
    normalize_chat_id,
)


def session_name_for_user(user):
    return (
        f'studyflow-{user.company_id}-{user.id}'
    )


def get_connected_account(company, user=None):
    queryset = WhatsAppAccount.objects.filter(
        company=company,
        is_connected=True,
    )

    if user:
        account = queryset.filter(user=user).first()

        if account:
            return account

    return queryset.order_by('-last_connected_at').first()


def connect_user_session(user, phone_number=''):
    client, _server = get_client_for_company(user.company)

    if not client:
        raise OpenWAError(
            'OpenWA server is not configured for this company. '
            'Set Base URL to http://localhost:2785/api and a valid API key.',
        )

    try:
        client.health_ready()
    except OpenWAError as exc:
        raise OpenWAError(
            'OpenWA gateway is unreachable. '
            'Start it with: docker compose -f docker-compose.dev.yml up -d --build openwa. '
            f'Details: {exc}',
        ) from exc

    account, _created = WhatsAppAccount.objects.get_or_create(
        user=user,
        defaults={
            'company': user.company,
            'phone_number': phone_number or f'pending-{user.id}',
            'session_id': f'pending-{user.id}',
        },
    )

    if phone_number:
        account.phone_number = phone_number

    name = session_name_for_user(user)
    session = None

    if account.session_id.startswith('pending-'):
        session = client.ensure_session(name)
        session_id = extract_session_id(session)

        if not session_id:
            raise OpenWAError(
                'OpenWA did not return a session id.',
            )

        account.session_id = session_id
    else:
        try:
            session = client.get_session(account.session_id)
        except OpenWAError:
            session = client.ensure_session(name)
            session_id = extract_session_id(session)

            if session_id:
                account.session_id = session_id

    client.safe_start_session(account.session_id)

    try:
        qr_raw = client.get_qr(account.session_id)
    except OpenWAError:
        qr_raw = {}

    qr = extract_qr_payload(qr_raw, session)
    account.is_connected = is_session_connected(
        session or {},
    )

    if account.is_connected:
        account.last_connected_at = timezone.now()

    account.save()

    return account, qr


def refresh_session_status(account):
    client, _server = get_client_for_company(account.company)

    if (
        not client
        or not account.session_id
        or account.session_id.startswith('pending-')
    ):
        return account

    try:
        session = client.get_session(account.session_id)
    except OpenWAError:
        account.is_connected = False
        account.save(update_fields=['is_connected'])
        return account

    account.is_connected = is_session_connected(session)

    if account.is_connected:
        account.last_connected_at = timezone.now()

    account.save(
        update_fields=[
            'is_connected',
            'last_connected_at',
        ],
    )

    return account


def send_whatsapp_message(
    *,
    company,
    user,
    recipient_number,
    message,
    message_type='manual',
    lead=None,
    student=None,
    account=None,
):
    client, _server = get_client_for_company(company)

    if not client:
        raise OpenWAError(
            'OpenWA server is not configured.',
        )

    account = account or get_connected_account(
        company,
        user=user,
    )

    if not account:
        raise OpenWAError(
            'No connected WhatsApp session found. '
            'Open WhatsApp settings and connect a session first.',
        )

    if not account.is_connected:
        refresh_session_status(account)

    if not account.is_connected:
        raise OpenWAError(
            'WhatsApp session is not connected. Scan the QR code first.',
        )

    chat_id = normalize_chat_id(recipient_number)

    record = WhatsAppMessage.objects.create(
        company=company,
        account=account,
        recipient_number=recipient_number,
        message=message,
        message_type=message_type,
        lead=lead,
        student=student,
        status='pending',
    )

    try:
        response = client.send_text(
            account.session_id,
            chat_id,
            message,
        )
        record.status = 'sent'
        record.response_data = str(response)[:2000]
    except OpenWAError as exc:
        record.status = 'failed'
        record.response_data = str(exc)[:2000]
        record.save()
        raise

    record.save()
    return record


def send_whatsapp_reminder(
    *,
    company,
    alert_key,
    recipient_number,
    message,
    message_type,
    lead=None,
    student=None,
):
    if not recipient_number:
        return False

    if WhatsAppReminderLog.objects.filter(
        alert_key=alert_key,
    ).exists():
        return False

    account = get_connected_account(company)

    if not account:
        return False

    try:
        send_whatsapp_message(
            company=company,
            user=account.user,
            recipient_number=recipient_number,
            message=message,
            message_type=message_type,
            lead=lead,
            student=student,
            account=account,
        )
    except OpenWAError:
        return False

    WhatsAppReminderLog.objects.create(
        company=company,
        alert_key=alert_key,
    )

    return True
