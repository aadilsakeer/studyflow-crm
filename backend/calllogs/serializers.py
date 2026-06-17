from rest_framework import serializers

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

    def get_called_by_name(self, obj):
        if not obj.called_by:
            return None

        return (
            obj.called_by.get_full_name()
            or obj.called_by.username
        )
