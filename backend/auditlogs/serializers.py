from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AuditLog
        fields = (
            "id",
            "company",
            "user",
            "module",
            "action",
            "object_id",
            "description",
            "created_at",
        )
        read_only_fields = (
            "company",
            "user",
            "module",
            "action",
            "object_id",
            "description",
            "created_at",
        )
