from datetime import timedelta

from django.db.models import Count, Q
from django.utils import timezone

from auditlogs.services import AuditLogService
from licensing.models import TenantSupportTicket

from .constants import (
    AUDIT_MODULE_OPERATIONS,
    PRIORITY_NORMAL,
    SLA_AT_RISK,
    SLA_BREACHED,
    SLA_HOURS,
    SLA_ON_TRACK,
    STATUS_CLOSED,
    STATUS_IN_PROGRESS,
    STATUS_OPEN,
    STATUS_RESOLVED,
    STATUS_WAITING,
    TICKET_TYPE_ESCALATION,
)
from .models import InternalComment, InternalTeamMember, InternalTicket


class InternalOperationsService:

    @classmethod
    def _audit(cls, *, company, user, action, object_id, description):
        if not company or not user:
            return
        AuditLogService.log(
            company=company,
            user=user,
            module=AUDIT_MODULE_OPERATIONS,
            action=action,
            object_id=object_id,
            description=description,
        )

    @classmethod
    def compute_sla(cls, ticket):
        hours = SLA_HOURS.get(ticket.priority, 48)
        if not ticket.sla_due and ticket.created_at:
            ticket.sla_due = ticket.created_at + timedelta(hours=hours)

        if ticket.status in (STATUS_RESOLVED, STATUS_CLOSED):
            ticket.sla_status = SLA_ON_TRACK
            return ticket

        if not ticket.sla_due:
            return ticket

        remaining = ticket.sla_due - timezone.now()
        if remaining.total_seconds() <= 0:
            ticket.sla_status = SLA_BREACHED
        elif remaining.total_seconds() <= hours * 3600 * 0.25:
            ticket.sla_status = SLA_AT_RISK
        else:
            ticket.sla_status = SLA_ON_TRACK
        return ticket

    @staticmethod
    def _user_brief(user):
        if not user:
            return None
        return {
            'id': user.id,
            'name': user.get_full_name() or user.username,
            'email': user.email,
        }

    @classmethod
    def serialize_ticket(cls, ticket, *, include_comments=False):
        data = {
            'id': ticket.id,
            'ticket_type': ticket.ticket_type,
            'title': ticket.title,
            'description': ticket.description,
            'priority': ticket.priority,
            'status': ticket.status,
            'assignee': cls._user_brief(ticket.assignee),
            'due_date': ticket.due_date,
            'sla_due': ticket.sla_due,
            'sla_status': ticket.sla_status,
            'company_id': ticket.company_id,
            'company_name': ticket.company.name if ticket.company else None,
            'source_support_ticket_id': ticket.source_support_ticket_id,
            'created_by': cls._user_brief(ticket.created_by),
            'created_at': ticket.created_at,
            'updated_at': ticket.updated_at,
            'resolved_at': ticket.resolved_at,
        }
        if include_comments:
            data['comments'] = [
                {
                    'id': c.id,
                    'body': c.body,
                    'author': cls._user_brief(c.author),
                    'created_at': c.created_at,
                }
                for c in ticket.comments.select_related('author').all()
            ]
            data['timeline'] = cls.ticket_timeline(ticket)
        return data

    @classmethod
    def ticket_timeline(cls, ticket):
        events = []
        for c in ticket.comments.select_related('author').all():
            events.append({
                'type': 'comment',
                'title': 'Internal comment',
                'body': c.body,
                'author': cls._user_brief(c.author),
                'created_at': c.created_at,
            })
        events.append({
            'type': 'ticket',
            'title': 'Ticket created',
            'body': ticket.title,
            'author': cls._user_brief(ticket.created_by),
            'created_at': ticket.created_at,
        })
        if ticket.source_support_ticket_id:
            st = ticket.source_support_ticket
            events.append({
                'type': 'escalation',
                'title': 'Escalated from support',
                'body': st.subject,
                'created_at': st.created_at,
            })
        events.sort(key=lambda e: e['created_at'] or timezone.now(), reverse=True)
        return events

    @classmethod
    def create_ticket(cls, *, actor, data):
        ticket = InternalTicket.objects.create(
            ticket_type=data.get('ticket_type', TICKET_TYPE_ESCALATION),
            title=data['title'],
            description=data.get('description', ''),
            priority=data.get('priority', PRIORITY_NORMAL),
            status=STATUS_OPEN,
            assignee_id=data.get('assignee_id'),
            due_date=data.get('due_date'),
            company_id=data.get('company_id'),
            created_by=actor,
        )
        cls.compute_sla(ticket)
        ticket.save()
        cls._audit(
            company=ticket.company,
            user=actor,
            action='create_internal_ticket',
            object_id=ticket.id,
            description=f'Created internal ticket: {ticket.title}',
        )
        return cls.serialize_ticket(ticket)

    @classmethod
    def assign_ticket(cls, *, ticket_id, actor, assignee_id=None, status=None):
        ticket = InternalTicket.objects.filter(pk=ticket_id).first()
        if not ticket:
            return None
        if assignee_id is not None:
            ticket.assignee_id = assignee_id or None
        if status:
            ticket.status = status
            if status in (STATUS_RESOLVED, STATUS_CLOSED) and not ticket.resolved_at:
                ticket.resolved_at = timezone.now()
            elif status in (STATUS_OPEN, STATUS_IN_PROGRESS):
                ticket.resolved_at = None
        cls.compute_sla(ticket)
        ticket.save()
        cls._audit(
            company=ticket.company,
            user=actor,
            action='assign_internal_ticket',
            object_id=ticket.id,
            description=f'Assigned/updated ticket #{ticket.id}',
        )
        return cls.serialize_ticket(ticket)

    @classmethod
    def add_comment(cls, *, ticket_id, actor, body):
        ticket = InternalTicket.objects.filter(pk=ticket_id).first()
        if not ticket:
            return None
        comment = InternalComment.objects.create(
            ticket=ticket,
            author=actor,
            body=body,
        )
        cls._audit(
            company=ticket.company,
            user=actor,
            action='internal_ticket_comment',
            object_id=ticket.id,
            description=f'Comment on ticket #{ticket.id}',
        )
        return {
            'id': comment.id,
            'body': comment.body,
            'author': cls._user_brief(actor),
            'created_at': comment.created_at,
        }

    @classmethod
    def escalate_support_ticket(cls, *, support_ticket_id, actor, assignee_id=None):
        support = TenantSupportTicket.objects.select_related('company').filter(
            pk=support_ticket_id,
        ).first()
        if not support:
            return None
        existing = InternalTicket.objects.filter(source_support_ticket=support).first()
        if existing:
            return cls.serialize_ticket(existing, include_comments=True)

        ticket = InternalTicket.objects.create(
            ticket_type=TICKET_TYPE_ESCALATION,
            title=f'Escalation: {support.subject}',
            description=support.description,
            priority=support.priority,
            status=STATUS_OPEN,
            assignee_id=assignee_id,
            company=support.company,
            source_support_ticket=support,
            created_by=actor,
        )
        cls.compute_sla(ticket)
        ticket.save()
        support.status = TenantSupportTicket.STATUS_IN_PROGRESS
        support.save(update_fields=['status', 'updated_at'])
        InternalComment.objects.create(
            ticket=ticket,
            author=actor,
            body=f'Escalated from tenant support ticket #{support.id}',
        )
        cls._audit(
            company=support.company,
            user=actor,
            action='escalate_support_ticket',
            object_id=ticket.id,
            description=f'Escalated support ticket #{support.id} to internal ops',
        )
        return cls.serialize_ticket(ticket, include_comments=True)

    @classmethod
    def list_tickets(cls, *, status=None, ticket_type=None, assignee_id=None):
        qs = InternalTicket.objects.select_related(
            'assignee', 'company', 'created_by',
        ).all()
        if status:
            qs = qs.filter(status=status)
        if ticket_type:
            qs = qs.filter(ticket_type=ticket_type)
        if assignee_id:
            qs = qs.filter(assignee_id=assignee_id)
        return [cls.serialize_ticket(t) for t in qs[:200]]

    @classmethod
    def get_ticket(cls, ticket_id):
        ticket = InternalTicket.objects.select_related(
            'assignee', 'company', 'created_by', 'source_support_ticket',
        ).filter(pk=ticket_id).first()
        if not ticket:
            return None
        return cls.serialize_ticket(ticket, include_comments=True)

    @classmethod
    def board(cls):
        columns = {s: [] for s in (
            STATUS_OPEN, STATUS_IN_PROGRESS, STATUS_WAITING,
            STATUS_RESOLVED, STATUS_CLOSED,
        )}
        for ticket in InternalTicket.objects.select_related('assignee').exclude(
            status=STATUS_CLOSED,
        ).order_by('-priority', '-created_at')[:100]:
            columns.get(ticket.status, columns[STATUS_OPEN]).append(
                cls.serialize_ticket(ticket),
            )
        return {'columns': columns}

    @classmethod
    def workload_dashboard(cls):
        open_q = ~Q(status__in=(STATUS_RESOLVED, STATUS_CLOSED))
        tickets = InternalTicket.objects.filter(open_q)
        by_type = dict(
            tickets.values('ticket_type').annotate(c=Count('id')).values_list('ticket_type', 'c'),
        )
        by_priority = dict(
            tickets.values('priority').annotate(c=Count('id')).values_list('priority', 'c'),
        )
        critical = tickets.filter(
            Q(priority='urgent') | Q(sla_status=SLA_BREACHED),
        ).count()
        team_load = []
        for member in InternalTeamMember.objects.filter(is_active=True).select_related('user'):
            assigned = InternalTicket.objects.filter(assignee=member.user).filter(open_q).count()
            team_load.append({
                'member': cls._user_brief(member.user),
                'team': member.team,
                'assigned_open': assigned,
                'capacity': member.weekly_capacity,
                'load_pct': min(100, round(assigned / member.weekly_capacity * 100, 1))
                if member.weekly_capacity else 0,
            })
        return {
            'totals': {
                'open_tickets': tickets.count(),
                'critical_incidents': critical,
                'escalations': tickets.filter(ticket_type=TICKET_TYPE_ESCALATION).count(),
                'sla_breached': tickets.filter(sla_status=SLA_BREACHED).count(),
            },
            'by_type': by_type,
            'by_priority': by_priority,
            'team_load': team_load,
            'recent': cls.list_tickets()[:10],
        }

    @classmethod
    def list_team(cls):
        return [
            {
                'id': m.id,
                'user': cls._user_brief(m.user),
                'team': m.team,
                'is_active': m.is_active,
                'weekly_capacity': m.weekly_capacity,
            }
            for m in InternalTeamMember.objects.filter(is_active=True).select_related('user')
        ]
