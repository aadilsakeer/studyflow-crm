from rest_framework import serializers

from .models import StudentTimeline


class StudentTimelineSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.SerializerMethodField()

    class Meta:
        model = StudentTimeline
        fields = '__all__'

    def get_performed_by_name(self, obj):
        if not obj.performed_by:
            return None

        return (
            obj.performed_by.get_full_name()
            or obj.performed_by.username
        )
