import json
import re
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


class OpenWAClient:

    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _request(self, method, path, body=None):
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
                timeout=60,
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
        except urllib.error.URLError as exc:
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

        return self.create_session(name)

    def safe_start_session(self, session_id):
        try:
            return self.start_session(session_id)
        except OpenWAError as exc:
            if '404' in str(exc) or 'Cannot POST' in str(exc):
                return {}
            raise


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
        image = qr_payload.get('image')
        code = qr_payload.get('code')

        if image or code:
            return {
                'image': image,
                'code': code,
                'qr': image or code,
            }

    if session_payload:
        image = session_payload.get('qr')

        if image:
            return {
                'image': image,
                'qr': image,
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


def normalize_chat_id(phone):
    digits = re.sub(r'\D', '', phone or '')

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
