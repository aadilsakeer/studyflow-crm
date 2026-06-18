from notifications.models import Notification

from .models import WorkflowAlertLog


def send_workflow_notification(
    *,
    company,
    user,
    alert_key,
    title,
    message,
    notification_type='warning',
):
    if not user or not company:
        return False

    exists = WorkflowAlertLog.objects.filter(
        alert_key=alert_key,
        user=user,
    ).exists()

    if exists:
        return False

    Notification.objects.create(
        company=company,
        user=user,
        title=title,
        message=message,
        notification_type=notification_type,
    )

    WorkflowAlertLog.objects.create(
        company=company,
        alert_key=alert_key,
        user=user,
    )

    return True
