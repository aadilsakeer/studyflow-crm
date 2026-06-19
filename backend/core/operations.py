import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.core.mail import send_mail
from django.db import connection

from .pg_dump import PgDumpNotFoundError, check_pg_dump, resolve_pg_dump_path, uses_postgresql


def validate_stripe_live():
    key = getattr(settings, 'STRIPE_SECRET_KEY', '')
    if not key:
        return {'ok': False, 'error': 'not_configured'}
    try:
        import stripe
        stripe.api_key = key
        acct = stripe.Account.retrieve()
        live = getattr(settings, 'STRIPE_LIVE_MODE', False)
        is_live_key = key.startswith('sk_live_')
        return {
            'ok': True,
            'live_mode_setting': live,
            'live_key': is_live_key,
            'account_id': acct.get('id'),
            'valid': live == is_live_key or not live,
        }
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def validate_razorpay_live():
    kid = getattr(settings, 'RAZORPAY_KEY_ID', '')
    secret = getattr(settings, 'RAZORPAY_KEY_SECRET', '')
    if not kid or not secret:
        return {'ok': False, 'error': 'not_configured'}
    try:
        import razorpay
        client = razorpay.Client(auth=(kid, secret))
        client.payment.all({'count': 1})
        return {'ok': True, 'key_id': kid[:8] + '...'}
    except Exception as exc:
        return {'ok': False, 'error': str(exc)}


def check_email_config():
    backend = getattr(settings, 'EMAIL_BACKEND', '')
    smtp = 'smtp' in backend.lower()
    configured = bool(getattr(settings, 'EMAIL_HOST', '')) or not smtp
    return {
        'backend': backend,
        'smtp_configured': configured,
        'from_email': getattr(settings, 'DEFAULT_FROM_EMAIL', ''),
    }


def verify_transactional_email(to_email):
    send_mail(
        'Globvio email verification',
        'Transactional email is working.',
        settings.DEFAULT_FROM_EMAIL,
        [to_email],
        fail_silently=False,
    )
    return True


def check_celery():
    try:
        from celery import current_app
        insp = current_app.control.inspect(timeout=2.0)
        ping = insp.ping() or {}
        active = insp.active() or {}
        reserved = insp.reserved() or {}
        failed_count = sum(len(v) for v in active.values())
        return {
            'ok': bool(ping),
            'workers': list(ping.keys()),
            'active_tasks': failed_count,
            'reserved_tasks': sum(len(v) for v in reserved.values()),
        }
    except Exception as exc:
        return {'ok': False, 'error': str(exc), 'workers': [], 'active_tasks': 0}


def check_sentry():
    dsn = os.getenv('SENTRY_DSN', '')
    return {'configured': bool(dsn)}


def run_db_backup():
    backup_dir = Path(getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups'))
    backup_dir.mkdir(parents=True, exist_ok=True)
    db = settings.DATABASES['default']
    ts = datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')
    outfile = backup_dir / f'backup_{ts}.sql'

    if uses_postgresql():
        pg_dump = resolve_pg_dump_path()
        if not pg_dump:
            raise PgDumpNotFoundError()

        env = os.environ.copy()
        if db.get('PASSWORD'):
            env['PGPASSWORD'] = db['PASSWORD']
        cmd = [
            pg_dump, '-h', db.get('HOST', 'localhost'),
            '-p', str(db.get('PORT', 5432)),
            '-U', db.get('USER', 'postgres'),
            '-d', db['NAME'], '-f', str(outfile),
        ]
        try:
            subprocess.run(cmd, env=env, check=True, capture_output=True)
        except FileNotFoundError as exc:
            raise PgDumpNotFoundError() from exc
    else:
        outfile = backup_dir / f'backup_{ts}.json'
        from django.core.management import call_command
        call_command('dumpdata', '--natural-foreign', '--natural-primary',
                     '-e', 'contenttypes', '-e', 'auth.Permission',
                     output=str(outfile))

    return {'path': str(outfile), 'size': outfile.stat().st_size}


def verify_latest_backup():
    backup_dir = Path(getattr(settings, 'BACKUP_DIR', settings.BASE_DIR / 'backups'))
    if not backup_dir.exists():
        return {'ok': False, 'error': 'no_backup_dir'}
    files = sorted(backup_dir.glob('backup_*'), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return {'ok': False, 'error': 'no_backups'}
    latest = files[0]
    size = latest.stat().st_size
    readable = size > 100
    return {'ok': readable, 'file': latest.name, 'size': size}


def test_restore_readiness():
    v = verify_latest_backup()
    if not v.get('ok'):
        return v
    backup_dir = Path(settings.BACKUP_DIR)
    latest = backup_dir / v['file']
    if latest.suffix == '.sql':
        content = latest.read_text(encoding='utf-8', errors='ignore')[:500]
        ok = 'PostgreSQL' in content or 'CREATE' in content or len(content) > 50
    else:
        ok = latest.stat().st_size > 50
    return {'ok': ok, 'file': v['file'], 'dry_run': True}


def operations_snapshot():
    health_db = True
    try:
        with connection.cursor() as c:
            c.execute('SELECT 1')
    except Exception:
        health_db = False

    stripe = validate_stripe_live()
    razorpay = validate_razorpay_live()
    email = check_email_config()
    celery = check_celery()
    backup = verify_latest_backup()
    pg_dump = check_pg_dump() if uses_postgresql() else {'ok': True, 'skipped': True}
    sentry = check_sentry()

    alerts = []
    if not health_db:
        alerts.append('database_down')
    if stripe.get('ok') and not stripe.get('valid', True):
        alerts.append('stripe_live_mode_mismatch')
    if not razorpay.get('ok') and getattr(settings, 'RAZORPAY_KEY_ID', ''):
        alerts.append('razorpay_invalid')
    if not backup.get('ok'):
        alerts.append('backup_missing')
    if uses_postgresql() and not pg_dump.get('ok'):
        alerts.append('pg_dump_missing')
    if not celery.get('ok'):
        alerts.append('celery_unreachable')

    status = 'healthy' if not alerts else 'degraded'
    return {
        'status': status,
        'database': {'ok': health_db},
        'payments': {'stripe': stripe, 'razorpay': razorpay},
        'email': email,
        'celery': celery,
        'sentry': sentry,
        'backup': backup,
        'pg_dump': pg_dump,
        'alerts': alerts,
        'timestamp': datetime.now(timezone.utc).isoformat(),
    }
