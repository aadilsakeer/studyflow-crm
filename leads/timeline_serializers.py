from rest_framework import serializers

from .models import LeadTimeline


class LeadTimelineSerializer(
    serializers.ModelSerializer,
):

    performed_by_name = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    class Meta:
        model = LeadTimeline
        fields = "__all__"

    def get_performed_by_name(self, obj):
        if not obj.performed_by:
            return None

        return (
            obj.performed_by.get_full_name()
            or obj.performed_by.username
        )
