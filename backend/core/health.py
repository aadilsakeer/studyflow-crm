import os
from datetime import datetime, timezone

from django.conf import settings
from django.db import connection


def check_database():
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        return {'ok': True}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def check_env():
    missing = []
    if not getattr(settings, 'SECRET_KEY', None):
        missing.append('SECRET_KEY')
    if not settings.DEBUG and not settings.ALLOWED_HOSTS:
        missing.append('ALLOWED_HOSTS')
    return {'ok': not missing, 'missing': missing}


def check_billing_config():
    stripe = bool(getattr(settings, 'STRIPE_SECRET_KEY', ''))
    razorpay = bool(getattr(settings, 'RAZORPAY_KEY_ID', ''))
    live = getattr(settings, 'STRIPE_LIVE_MODE', False)
    return {
        'stripe_configured': stripe,
        'razorpay_configured': razorpay,
        'stripe_live_mode': live,
    }


def check_backup_status():
    backup_dir = getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups')
    path = backup_dir if hasattr(backup_dir, 'exists') else settings.BASE_DIR / 'backups'
    exists = path.exists()
    latest = None
    if exists:
        files = sorted(path.glob('*'), key=lambda p: p.stat().st_mtime, reverse=True)
        if files:
            latest = datetime.fromtimestamp(
                files[0].stat().st_mtime,
                tz=timezone.utc,
            ).isoformat()
    return {'backup_dir_exists': exists, 'latest_backup': latest}


def health_snapshot():
    db = check_database()
    env = check_env()
    return {
        'status': 'healthy' if db['ok'] and env['ok'] else 'degraded',
        'database': db,
        'environment': env,
        'billing': check_billing_config(),
        'backups': check_backup_status(),
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
