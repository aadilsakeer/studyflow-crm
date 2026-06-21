import json
import re
import time
import urllib.error
import urllib.request


class OpenWAError(Exception):
    pass


CONNECTED_STATUSES = {
    'connected',
    'ready',
    'working',
    'open',
    'CONNECTED',
    'READY',
}

DEFAULT_REQUEST_TIMEOUT = 60
START_REQUEST_TIMEOUT = 120
SEND_REQUEST_TIMEOUT = 180


class OpenWAClient:

    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _request(self, method, path, body=None, timeout=DEFAULT_REQUEST_TIMEOUT):
        url = f'{self.base_url}{path}'
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        data = None

        if body is not None:
            data = json.dumps(body).encode('utf-8')

        request = urllib.request.Request(
            url,
            data=data,
            headers=headers,
            method=method,
        )

        try:
            with urllib.request.urlopen(
                request,
                timeout=timeout,
            ) as response:
                raw = response.read().decode('utf-8')

                if not raw:
                    return {}

                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode('utf-8')
            raise OpenWAError(
                f'HTTP {exc.code}: {raw or exc.reason}',
            ) from exc
        except TimeoutError as exc:
            raise OpenWAError(
                'OpenWA request timed out. The WhatsApp gateway may still be '
                'processing — wait a moment and try again.',
            ) from exc
        except urllib.error.URLError as exc:
            if isinstance(exc.reason, TimeoutError):
                raise OpenWAError(
                    'OpenWA request timed out. The WhatsApp gateway may still be '
                    'processing — wait a moment and try again.',
                ) from exc

            raise OpenWAError(str(exc)) from exc

    def health_ready(self):
        return self._request('GET', '/health/ready')

    def list_sessions(self):
        data = self._request('GET', '/sessions')

        if isinstance(data, list):
            return data

        return data.get('results', data.get('data', []))

    def create_session(self, name):
        return self._request(
            'POST',
            '/sessions',
            {'name': name},
        )

    def start_session(self, session_id):
        return self._request(
            'POST',
            f'/sessions/{session_id}/start',
            timeout=START_REQUEST_TIMEOUT,
        )

    def stop_session(self, session_id):
        return self._request(
            'POST',
            f'/sessions/{session_id}/stop',
        )

    def delete_session(self, session_id):
        return self._request(
            'DELETE',
            f'/sessions/{session_id}',
        )

    def get_session(self, session_id):
        return self._request(
            'GET',
            f'/sessions/{session_id}',
        )

    def get_qr(self, session_id):
        return self._request(
            'GET',
            f'/sessions/{session_id}/qr',
        )

    def send_text(self, session_id, chat_id, text):
        return self._request(
            'POST',
            f'/sessions/{session_id}/messages/send-text',
            {
                'chatId': chat_id,
                'text': text,
            },
            timeout=SEND_REQUEST_TIMEOUT,
        )

    def find_session_by_name(self, name):
        for session in self.list_sessions():
            if session.get('name') == name:
                return session

        return None

    def ensure_session(self, name):
        existing = self.find_session_by_name(name)

        if existing and existing.get('id'):
            return existing

        try:
            return self.create_session(name)
        except OpenWAError as exc:
            if '409' in str(exc) or 'already exists' in str(exc).lower():
                existing = self.find_session_by_name(name)

                if existing:
                    return existing

            raise

    def safe_start_session(self, session_id):
        return start_session_for_qr(self, session_id)


def is_session_missing_error(exc):
    message = str(exc).lower()

    return (
        '404' in str(exc)
        or 'not found' in message
        or 'session not found' in message
    )


def is_session_already_started_error(exc):
    return 'already started' in str(exc).lower()


def is_qr_not_ready_error(exc):
    message = str(exc).lower()

    return (
        'not ready' in message
        or 'not started' in message
        or 'please wait' in message
    )


def is_browser_launch_error(exc):
    message = str(exc).lower()

    return (
        'failed to launch the browser' in message
        or 'profile appears to be in use' in message
        or 'process_singleton' in message
    )


def start_session_for_qr(client, session_id):
    session = None

    try:
        session = client.get_session(session_id)
        status = str(session.get('status', '')).lower()

        if status in {
            'qr_ready',
            'ready',
            'initializing',
            'authenticating',
        }:
            return session

        if status in {'failed', 'disconnected'}:
            try:
                client.stop_session(session_id)
            except OpenWAError:
                pass

            time.sleep(1.5)
    except OpenWAError:
        pass

    try:
        return client.start_session(session_id)
    except OpenWAError as exc:
        if is_session_already_started_error(exc):
            return session or {}

        if '404' in str(exc) or 'Cannot POST' in str(exc):
            return {}

        raise


def fetch_session_qr(
    client,
    session_id,
    session_payload=None,
    *,
    max_attempts=10,
    delay_seconds=0.75,
):
    """
    Match verify_openwa_integration.py: start the session engine, then poll
    until OpenWA exposes a QR image (status moves from created -> qr_ready).
    """
    start_session_for_qr(client, session_id)

    session = session_payload
    last_exc = None

    for attempt in range(max_attempts):
        if attempt:
            time.sleep(delay_seconds)

        try:
            qr_raw = client.get_qr(session_id)
            qr = extract_qr_payload(qr_raw, session)

            if qr.get('image') or qr.get('code') or qr.get('qr'):
                return qr
        except OpenWAError as exc:
            last_exc = exc

            if is_session_missing_error(exc):
                raise

            if not is_qr_not_ready_error(exc):
                raise

        try:
            session = client.get_session(session_id)
            qr = extract_qr_payload({}, session)

            if qr.get('image') or qr.get('code') or qr.get('qr'):
                return qr
        except OpenWAError as exc:
            last_exc = exc

            if is_session_missing_error(exc):
                raise

    if last_exc:
        raise last_exc

    return extract_qr_payload({}, session)


def extract_session_id(session_payload):
    if not session_payload:
        return None

    return (
        session_payload.get('id')
        or session_payload.get('sessionId')
        or session_payload.get('name')
    )


def extract_qr_payload(qr_payload, session_payload=None):
    if qr_payload:
        image = (
            qr_payload.get('qrCode')
            or qr_payload.get('qr_code')
            or qr_payload.get('image')
            or qr_payload.get('qr')
        )
        code = qr_payload.get('code')

        if image or code:
            return {
                'image': image,
                'code': code,
                'qr': image or code,
                'status': qr_payload.get('status'),
            }

    if session_payload:
        image = (
            session_payload.get('qrCode')
            or session_payload.get('qr')
            or session_payload.get('qr_code')
        )

        if image:
            return {
                'image': image,
                'qr': image,
                'status': session_payload.get('status'),
            }

    return {}


def is_session_connected(session_payload):
    status = (
        session_payload.get('status')
        or session_payload.get('state')
        or ''
    )

    return str(status).upper() in {
        item.upper() for item in CONNECTED_STATUSES
    }


def humanize_openwa_error(exc):
    message = str(exc)

    if is_browser_launch_error(exc):
        return (
            'OpenWA could not start the WhatsApp browser (stale Chromium lock '
            'after restart). Restart the OpenWA container, then click Connect again.'
        )

    if 'No LID for user' in message:
        return (
            'WhatsApp could not open a chat with this number. '
            'Use full international format (e.g. 91XXXXXXXXXX), or send '
            'one message to this contact from your phone first, then retry.'
        )

    return message


def describe_openwa_session_error(session_payload):
    if not session_payload:
        return None

    last_error = session_payload.get('lastError') or ''

    if last_error and is_browser_launch_error(OpenWAError(last_error)):
        return humanize_openwa_error(OpenWAError(last_error))

    status = str(session_payload.get('status', '')).lower()

    if status == 'failed' and last_error:
        return (
            'WhatsApp session failed to start. '
            f'{last_error[:400]}'
        )

    return None


def enrich_openwa_error(client, session_id, exc):
    if is_browser_launch_error(exc):
        return humanize_openwa_error(exc)

    try:
        session = client.get_session(session_id)
        detail = describe_openwa_session_error(session)

        if detail:
            return detail
    except OpenWAError:
        pass

    return humanize_openwa_error(exc)


def normalize_chat_id(phone, sender_phone=''):
    digits = re.sub(r'\D', '', phone or '')
    sender_digits = re.sub(r'\D', '', sender_phone or '')

    if (
        len(digits) == 10
        and len(sender_digits) > 10
        and not sender_digits.startswith('pending')
    ):
        cc_len = len(sender_digits) - 10
        if 1 <= cc_len <= 3:
            digits = sender_digits[:cc_len] + digits

    if not digits:
        raise ValueError('Phone number is required.')

    return f'{digits}@c.us'


def normalize_base_url(base_url):
    base_url = base_url.rstrip('/')

    if base_url.endswith('/api'):
        return base_url

    return f'{base_url}/api'


def get_client_for_company(company):
    from .models import WhatsAppServer

    server = WhatsAppServer.objects.filter(
        company=company,
        is_active=True,
    ).first()

    if not server or not server.base_url or not server.api_key:
        return None, None

    return OpenWAClient(
        normalize_base_url(server.base_url),
        server.api_key,
    ), server
