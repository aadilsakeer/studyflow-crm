from celery import shared_task

from .operations import run_db_backup, verify_latest_backup


@shared_task(name='core.run_scheduled_backup')
def run_scheduled_backup():
    result = run_db_backup()
    verify = verify_latest_backup()
    return {'backup': result, 'verify': verify}
