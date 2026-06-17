from rest_framework import serializers

from accounts.services.permission_service import (
    get_user_permission_codes,
)

from .models import CustomUser


class CurrentUserSerializer(
    serializers.ModelSerializer,
):
    display_name = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    role_name = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()

    class Meta:
        model = CustomUser
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "display_name",
            "company_name",
            "role_name",
            "permissions",
            "is_superuser",
        )

    def get_display_name(self, obj):
        full_name = (
            f"{obj.first_name} {obj.last_name}".strip()
        )

        return full_name or obj.username

    def get_company_name(self, obj):
        if obj.company:
            return obj.company.name

        return None

    def get_role_name(self, obj):
        if obj.role:
            return obj.role.name

        return None

    def get_permissions(self, obj):
        return sorted(
            get_user_permission_codes(obj)
        )
