from django.utils import timezone

from rest_framework import serializers

from leads.models import FollowUp


class FollowUpSerializer(
    serializers.ModelSerializer,
):

    lead_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = FollowUp
        fields = "__all__"
        read_only_fields = (
            "completed_at",
        )

    def get_lead_name(self, obj):
        return (
            f"{obj.lead.first_name} "
            f"{obj.lead.last_name}".strip()
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
