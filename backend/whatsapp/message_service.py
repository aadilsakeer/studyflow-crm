from django.utils import timezone

from .models import WhatsAppAccount, WhatsAppMessage, WhatsAppReminderLog
from .openwa_client import (
    OpenWAError,
    extract_session_id,
    fetch_session_qr,
    get_client_for_company,
    enrich_openwa_error,
    humanize_openwa_error,
    is_browser_launch_error,
    is_session_connected,
    is_session_missing_error,
    normalize_chat_id,
    start_session_for_qr,
)


def session_name_for_user(user):
    return (
        f'studyflow-{user.company_id}-{user.id}'
    )


def get_connected_account(company, user=None):
    queryset = WhatsAppAccount.objects.filter(
        company=company,
    )

    if user:
        account = queryset.filter(user=user).first()

        if account:
            return account

    return queryset.filter(
        is_connected=True,
    ).order_by('-last_connected_at').first()


def _ensure_session_ready_for_send(client, account):
    if (
        not account.session_id
        or account.session_id.startswith('pending-')
    ):
        raise OpenWAError(
            'WhatsApp session is not connected. Scan the QR code first.',
        )

    session = client.get_session(account.session_id)
    status = str(session.get('status', '')).lower()

    if status == 'ready' and is_session_connected(session):
        account.is_connected = True
        account.last_connected_at = timezone.now()
        account.save(
            update_fields=[
                'is_connected',
                'last_connected_at',
            ],
        )
        return session

    start_session_for_qr(client, account.session_id)

    session = client.get_session(account.session_id)
    account.is_connected = is_session_connected(session)

    if account.is_connected:
        account.last_connected_at = timezone.now()

    account.save(
        update_fields=[
            'is_connected',
            'last_connected_at',
        ],
    )

    if not account.is_connected:
        raise OpenWAError(
            'WhatsApp session is not connected. Scan the QR code first.',
        )

    return session


def _pending_session_id(user):
    return f'pending-{user.id}'


def _clear_stale_session(account, user):
    account.session_id = _pending_session_id(user)
    account.is_connected = False
    account.last_connected_at = None


def _resolve_openwa_session(client, account, user):
    name = session_name_for_user(user)

    if account.session_id.startswith('pending-'):
        return client.ensure_session(name)

    try:
        return client.get_session(account.session_id)
    except OpenWAError as exc:
        if not is_session_missing_error(exc):
            raise

    session = client.find_session_by_name(name)

    if session:
        return session

    _clear_stale_session(account, user)
    return client.ensure_session(name)


def _fetch_session_qr_with_recovery(client, account, user, session_id, session):
    try:
        return fetch_session_qr(client, session_id, session)
    except OpenWAError as exc:
        if not is_browser_launch_error(exc):
            raise

        try:
            client.delete_session(session_id)
        except OpenWAError:
            pass

        _clear_stale_session(account, user)
        session = _resolve_openwa_session(client, account, user)
        session_id = extract_session_id(session)

        if not session_id:
            raise OpenWAError(
                'OpenWA did not return a session id after browser recovery.',
            ) from exc

        account.session_id = session_id
        return fetch_session_qr(client, session_id, session)


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

    session = _resolve_openwa_session(client, account, user)
    session_id = extract_session_id(session)

    if not session_id:
        raise OpenWAError(
            'OpenWA did not return a session id.',
        )

    account.session_id = session_id

    try:
        qr = _fetch_session_qr_with_recovery(
            client,
            account,
            user,
            session_id,
            session,
        )
    except OpenWAError as exc:
        raise OpenWAError(
            enrich_openwa_error(client, account.session_id, exc),
        ) from exc

    try:
        session = client.get_session(session_id)
    except OpenWAError:
        pass

    account.is_connected = is_session_connected(session or {})

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
    except OpenWAError as exc:
        if is_session_missing_error(exc):
            _clear_stale_session(account, account.user)
            account.save(
                update_fields=[
                    'session_id',
                    'is_connected',
                    'last_connected_at',
                ],
            )
            return account

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

    from licensing.constants import LIMIT_WHATSAPP
    from licensing.usage_service import UsageLimitService

    UsageLimitService.check(company, LIMIT_WHATSAPP)

    if not account:
        raise OpenWAError(
            'No WhatsApp session found. '
            'Open WhatsApp settings and connect a session first.',
        )

    refresh_session_status(account)

    _ensure_session_ready_for_send(client, account)

    try:
        chat_id = normalize_chat_id(
            recipient_number,
            account.phone_number,
        )
    except ValueError as exc:
        raise OpenWAError(str(exc)) from exc

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
        _log_whatsapp_audit(company, user, record)
        raise OpenWAError(
            enrich_openwa_error(client, account.session_id, exc),
        ) from exc

    record.save()
    _log_whatsapp_audit(company, user, record)
    return record


def _log_whatsapp_audit(company, user, record):
    from auditlogs.services import AuditLogService

    AuditLogService.log(
        company=company,
        user=user,
        module='WhatsApp',
        action='create',
        object_id=record.id,
        description=(
            f"WhatsApp {record.status} to "
            f"{record.recipient_number}"
        ),
    )


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
