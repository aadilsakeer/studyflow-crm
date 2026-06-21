from django.conf import settings
from django.db import models

from core.models import Company

from .constants import (
    PRIORITIES,
    PRIORITY_NORMAL,
    SLA_ON_TRACK,
    SLA_STATUSES,
    STATUSES,
    STATUS_OPEN,
    TEAMS,
    TICKET_TYPES,
    TICKET_TYPE_BUG,
)


class InternalTeamMember(models.Model):

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='internal_team_profile',
    )
    team = models.CharField(max_length=30, choices=[(t, t.replace('_', ' ').title()) for t in TEAMS])
    is_active = models.BooleanField(default=True)
    weekly_capacity = models.PositiveSmallIntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['team', 'user__username']

    def __str__(self):
        return f'{self.user} ({self.team})'


class InternalTicket(models.Model):

    ticket_type = models.CharField(
        max_length=20,
        choices=[(t, t.replace('_', ' ').title()) for t in TICKET_TYPES],
        default=TICKET_TYPE_BUG,
    )
    title = models.CharField(max_length=255)
    description = models.TextField()
    priority = models.CharField(
        max_length=20,
        choices=[(p, p.title()) for p in PRIORITIES],
        default=PRIORITY_NORMAL,
    )
    status = models.CharField(
        max_length=20,
        choices=[(s, s.replace('_', ' ').title()) for s in STATUSES],
        default=STATUS_OPEN,
    )
    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_internal_tickets',
    )
    due_date = models.DateField(null=True, blank=True)
    sla_due = models.DateTimeField(null=True, blank=True)
    sla_status = models.CharField(
        max_length=20,
        choices=[(s, s.replace('_', ' ').title()) for s in SLA_STATUSES],
        default=SLA_ON_TRACK,
    )
    company = models.ForeignKey(
        Company,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='internal_tickets',
    )
    source_support_ticket = models.ForeignKey(
        'licensing.TenantSupportTicket',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='internal_escalations',
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_internal_tickets',
    )
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'#{self.pk} {self.title}'


class InternalComment(models.Model):

    ticket = models.ForeignKey(
        InternalTicket,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='internal_comments',
    )
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Comment on #{self.ticket_id}'
