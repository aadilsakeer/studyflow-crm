from django.utils import timezone

from .models import WhatsAppAccount, WhatsAppMessage, WhatsAppReminderLog
from .openwa_client import OpenWAError, get_client_for_company, normalize_chat_id


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
    client, server = get_client_for_company(user.company)

    if not client:
        raise OpenWAError(
            'OpenWA server is not configured for this company.',
        )

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

    if account.session_id.startswith('pending-'):
        session = client.create_session(name)
        account.session_id = (
            session.get('id')
            or session.get('sessionId')
            or session.get('name')
            or name
        )

    client.start_session(account.session_id)

    try:
        qr = client.get_qr(account.session_id)
    except OpenWAError:
        qr = {}

    account.save()

    return account, qr


def refresh_session_status(account):
    client, _server = get_client_for_company(account.company)

    if not client or not account.session_id:
        return account

    try:
        session = client.get_session(account.session_id)
    except OpenWAError:
        account.is_connected = False
        account.save(update_fields=['is_connected'])
        return account

    status = (
        session.get('status')
        or session.get('state')
        or ''
    ).lower()

    connected = status in (
        'connected',
        'ready',
        'working',
        'open',
    )

    account.is_connected = connected

    if connected:
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
            'No connected WhatsApp session found.',
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
