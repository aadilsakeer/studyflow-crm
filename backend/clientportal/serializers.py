from rest_framework import serializers

from .models import ClientPortalAccess


class ClientPortalAccessSerializer(
    serializers.ModelSerializer
):

    password = serializers.CharField(
        write_only=True,
        required=False,
    )

    class Meta:
        model = ClientPortalAccess
        fields = (
            "id",
            "student",
            "username",
            "password",
            "is_active",
            "last_login",
            "created_at",
        )
        read_only_fields = (
            "last_login",
            "created_at",
        )
