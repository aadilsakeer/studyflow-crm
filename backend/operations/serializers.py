from rest_framework import serializers

from .constants import PRIORITIES, STATUSES, TICKET_TYPES


class InternalTicketCreateSerializer(serializers.Serializer):
    ticket_type = serializers.ChoiceField(choices=TICKET_TYPES, required=False)
    title = serializers.CharField(max_length=255)
    description = serializers.CharField(required=False, allow_blank=True)
    priority = serializers.ChoiceField(choices=PRIORITIES, required=False)
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    due_date = serializers.DateField(required=False, allow_null=True)
    company_id = serializers.IntegerField(required=False, allow_null=True)


class InternalTicketUpdateSerializer(serializers.Serializer):
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=STATUSES, required=False)
    priority = serializers.ChoiceField(choices=PRIORITIES, required=False)
    due_date = serializers.DateField(required=False, allow_null=True)


class InternalCommentCreateSerializer(serializers.Serializer):
    body = serializers.CharField()


class EscalateSupportSerializer(serializers.Serializer):
    support_ticket_id = serializers.IntegerField()
    assignee_id = serializers.IntegerField(required=False, allow_null=True)
