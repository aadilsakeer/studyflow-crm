import json
import re
import urllib.error
import urllib.request


class OpenWAError(Exception):
    pass


class OpenWAClient:

    def __init__(self, base_url, api_key):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def _request(self, method, path, body=None):
        url = f'{self.base_url}{path}'
        headers = {
            'X-API-Key': self.api_key,
            'Content-Type': 'application/json',
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
                timeout=30,
            ) as response:
                raw = response.read().decode('utf-8')

                if not raw:
                    return {}

                return json.loads(raw)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode('utf-8')
            raise OpenWAError(raw or str(exc)) from exc
        except urllib.error.URLError as exc:
            raise OpenWAError(str(exc)) from exc

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


def normalize_chat_id(phone):
    digits = re.sub(r'\D', '', phone or '')

    if not digits:
        raise ValueError('Phone number is required.')

    return f'{digits}@c.us'


def get_client_for_company(company):
    from .models import WhatsAppServer

    server = WhatsAppServer.objects.filter(
        company=company,
        is_active=True,
    ).first()

    if not server or not server.base_url or not server.api_key:
        return None, None

    base_url = server.base_url.rstrip('/')

    if not base_url.endswith('/api'):
        base_url = f'{base_url}/api'

    return OpenWAClient(
        base_url,
        server.api_key,
    ), server
