from django.utils import timezone

from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_lead_in_company,
)

from leads.models import FollowUp


class FollowUpSerializer(
    serializers.ModelSerializer,
):

    lead_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = FollowUp
        fields = (
            "id",
            "lead",
            "assigned_to",
            "follow_up_date",
            "notes",
            "completed",
            "completed_at",
            "lead_name",
        )
        read_only_fields = (
            "completed_at",
        )

    def get_lead_name(self, obj):
        return (
            f"{obj.lead.first_name} "
            f"{obj.lead.last_name}".strip()
        )

    def validate_lead(self, lead):
        company = get_request_company(
            self.context,
        )
        return validate_lead_in_company(
            lead,
            company,
        )

    def update(self, instance, validated_data):
        completed = validated_data.get(
            "completed",
            instance.completed,
        )

        if completed and not instance.completed:
            validated_data["completed_at"] = (
                timezone.now()
            )
        elif not completed:
            validated_data["completed_at"] = None

        return super().update(
            instance,
            validated_data,
        )
