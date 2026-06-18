#!/usr/bin/env python
"""
Verify OpenWA gateway compatibility with StudyFlow CRM client.

Usage:
  python scripts/verify_openwa_integration.py
  python scripts/verify_openwa_integration.py --send 919876543210 "Test message"
"""

import argparse
import json
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BACKEND_DIR))

from whatsapp.openwa_client import (  # noqa: E402
    OpenWAClient,
    extract_qr_payload,
    extract_session_id,
    is_session_connected,
    normalize_base_url,
)


DEFAULT_BASE_URL = 'http://localhost:2785/api'
DEFAULT_API_KEY = 'globvio-openwa-key'
SESSION_NAME = 'studyflow-verify'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--base-url',
        default=DEFAULT_BASE_URL,
    )
    parser.add_argument(
        '--api-key',
        default=DEFAULT_API_KEY,
    )
    parser.add_argument(
        '--send',
        nargs=2,
        metavar=('PHONE', 'MESSAGE'),
        help='Send a test message after session is connected',
    )
    args = parser.parse_args()

    client = OpenWAClient(
        normalize_base_url(args.base_url),
        args.api_key,
    )

    print('OpenWA integration verification')
    print(f'  Base URL: {client.base_url}')
    print(f'  API Key:  {args.api_key[:8]}...')

    health = client.health_ready()
    print(f'  Health:   OK ({json.dumps(health)[:120]})')

    session = client.ensure_session(SESSION_NAME)
    session_id = extract_session_id(session)
    print(f'  Session:  {session_id} status={session.get("status")}')

    client.safe_start_session(session_id)

    try:
        qr_raw = client.get_qr(session_id)
    except Exception as exc:
        qr_raw = {}
        print(f'  QR fetch: deferred ({exc})')

    qr = extract_qr_payload(qr_raw, session)
    has_qr = bool(qr.get('image') or qr.get('code') or qr.get('qr'))
    print(f'  QR ready: {has_qr}')

    session = client.get_session(session_id)
    connected = is_session_connected(session)
    print(f'  Connected: {connected} status={session.get("status")}')

    if args.send:
        if not connected:
            print(
                '  Send skipped: session not connected — scan QR in CRM or OpenWA dashboard first.',
            )
            return 1

        phone, message = args.send
        from whatsapp.openwa_client import normalize_chat_id

        chat_id = normalize_chat_id(phone)
        result = client.send_text(session_id, chat_id, message)
        print(f'  Send:     OK {json.dumps(result)[:200]}')
        return 0

    if not has_qr and not connected:
        print(
            '  Result:   Gateway reachable; scan QR to finish login.',
        )
        return 0

    print('  Result:   Gateway API matches CRM client expectations.')
    return 0


if __name__ == '__main__':
    try:
        raise SystemExit(main())
    except Exception as exc:
        print(f'FAILED: {exc}', file=sys.stderr)
        raise SystemExit(1) from exc
