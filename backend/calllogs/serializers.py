from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_lead_in_company,
)

from leads.models import CallLog


class CallLogSerializer(serializers.ModelSerializer):

    called_by_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = CallLog
        fields = "__all__"
        read_only_fields = (
            "call_time",
            "called_by",
        )

    def validate_lead(self, lead):
        company = get_request_company(
            self.context,
        )
        return validate_lead_in_company(
            lead,
            company,
        )

    def get_called_by_name(self, obj):
        if not obj.called_by:
            return None

        return (
            obj.called_by.get_full_name()
            or obj.called_by.username
        )
