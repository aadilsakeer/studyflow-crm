from rest_framework import serializers

from .models import LeadAuditLog


class LeadAuditLogSerializer(
    serializers.ModelSerializer,
):

    changed_by_name = (
        serializers.SerializerMethodField(
            read_only=True,
        )
    )

    class Meta:
        model = LeadAuditLog
        fields = "__all__"

    def get_changed_by_name(self, obj):
        if not obj.changed_by:
            return None

        return (
            obj.changed_by.get_full_name()
            or obj.changed_by.username
        )
