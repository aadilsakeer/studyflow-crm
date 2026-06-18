from celery import shared_task

from .reminder_service import run_all_reminders


@shared_task(name='automation.dispatch_workflow_reminders')
def dispatch_workflow_reminders():
    return run_all_reminders()
