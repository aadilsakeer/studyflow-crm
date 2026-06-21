from datetime import timedelta

from django.utils import timezone

from .models import (
    TenantSupportAttachment,
    TenantSupportMessage,
    TenantSupportTicket,
)
from .billing_notifications import notify_ticket_created, notify_ticket_reply

SLA_HOURS = {
    TenantSupportTicket.PRIORITY_LOW: 48,
    TenantSupportTicket.PRIORITY_NORMAL: 24,
    TenantSupportTicket.PRIORITY_HIGH: 8,
    TenantSupportTicket.PRIORITY_URGENT: 4,
}


class SupportDeskService:

    @classmethod
    def compute_sla(cls, ticket):
        hours = SLA_HOURS.get(ticket.priority, 24)
        if not ticket.sla_due_at and ticket.created_at:
            ticket.sla_due_at = ticket.created_at + timedelta(hours=hours)

        if ticket.status in (
            TenantSupportTicket.STATUS_RESOLVED,
            TenantSupportTicket.STATUS_CLOSED,
        ):
            ticket.sla_status = TenantSupportTicket.SLA_ON_TRACK
            return ticket

        if not ticket.sla_due_at:
            return ticket

        now = timezone.now()
        remaining = ticket.sla_due_at - now

        if remaining.total_seconds() <= 0:
            ticket.sla_status = TenantSupportTicket.SLA_BREACHED
        elif remaining.total_seconds() <= hours * 3600 * 0.25:
            ticket.sla_status = TenantSupportTicket.SLA_AT_RISK
        else:
            ticket.sla_status = TenantSupportTicket.SLA_ON_TRACK

        return ticket

    @classmethod
    def create_ticket(cls, *, company, user, subject, description, priority=None):
        ticket = TenantSupportTicket.objects.create(
            company=company,
            created_by=user,
            subject=subject,
            description=description,
            priority=priority or TenantSupportTicket.PRIORITY_NORMAL,
        )
        cls.compute_sla(ticket)
        ticket.save(update_fields=['sla_due_at', 'sla_status'])

        TenantSupportMessage.objects.create(
            ticket=ticket,
            author=user,
            body=description,
        )
        notify_ticket_created(ticket)
        return ticket

    @classmethod
    def add_message(cls, *, ticket, user, body, is_internal=False):
        if is_internal and not user.is_superuser:
            is_internal = False

        msg = TenantSupportMessage.objects.create(
            ticket=ticket,
            author=user,
            body=body,
            is_internal=is_internal,
        )
        if not is_internal:
            notify_ticket_reply(ticket, body)
        return msg

    @classmethod
    def add_attachment(cls, *, ticket, user, uploaded_file, message=None):
        return TenantSupportAttachment.objects.create(
            ticket=ticket,
            message=message,
            file=uploaded_file,
            filename=uploaded_file.name,
            uploaded_by=user,
        )

    @classmethod
    def refresh_sla(cls, ticket):
        ticket = cls.compute_sla(ticket)
        ticket.save(update_fields=['sla_status', 'updated_at'])
        return ticket
