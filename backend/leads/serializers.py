from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_branch_in_company,
    validate_user_in_company,
)

from .models import Lead


class LeadSerializer(serializers.ModelSerializer):

    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True,
    )
    assigned_to_name = serializers.SerializerMethodField(
        read_only=True,
    )
    assigned_counsellor_name = serializers.SerializerMethodField(
        read_only=True,
    )

    class Meta:
        model = Lead
        fields = (
            "id",
            "company",
            "branch",
            "first_name",
            "last_name",
            "phone",
            "email",
            "country_interest",
            "city",
            "visa_type",
            "budget",
            "source",
            "assigned_to",
            "assigned_to_name",
            "assigned_at",
            "assigned_counsellor",
            "assigned_counsellor_name",
            "counsellor_assigned_at",
            "qualified_at",
            "qualified_by",
            "profile_evaluation_notes",
            "recommended_countries",
            "recommended_universities",
            "application_readiness",
            "tags",
            "status",
            "status_display",
            "score",
            "remarks",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
            "updated_at",
        )
        read_only_fields = (
            "company",
            "score",
            "status_display",
            "assigned_to_name",
            "assigned_counsellor_name",
            "assigned_at",
            "counsellor_assigned_at",
            "qualified_at",
            "qualified_by",
            "is_deleted",
            "deleted_at",
            "deleted_by",
            "created_at",
            "updated_at",
        )

    def get_assigned_to_name(self, obj):
        if not obj.assigned_to:
            return None

        return (
            obj.assigned_to.get_full_name()
            or obj.assigned_to.username
        )

    def get_assigned_counsellor_name(self, obj):
        if not obj.assigned_counsellor:
            return None

        return (
            obj.assigned_counsellor.get_full_name()
            or obj.assigned_counsellor.username
        )

    def _get_company(self):
        if self.instance and self.instance.company_id:
            return self.instance.company

        request = self.context.get("request")

        if request and request.user.is_authenticated:
            return getattr(
                request.user,
                "company",
                None,
            )

        return None

    def validate_email(self, value):
        if value in ("", None):
            return None
        return value

    def validate_phone(self, value):
        company = self._get_company()

        queryset = Lead.objects.filter(
            phone=value,
        )

        if company:
            queryset = queryset.filter(
                company=company,
            )

        if self.instance:
            queryset = queryset.exclude(
                pk=self.instance.pk,
            )

        if queryset.exists():
            raise serializers.ValidationError(
                "A lead with this phone number "
                "already exists in your company."
            )

        return value

    def validate_assigned_to(self, value):
        return validate_user_in_company(
            value,
            self._get_company(),
        )

    def validate_assigned_counsellor(self, value):
        return validate_user_in_company(
            value,
            self._get_company(),
        )

    def validate_branch(self, value):
        return validate_branch_in_company(
            value,
            self._get_company(),
        )

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        lead = Lead.objects.create(**validated_data)
        if tags:
            lead.tags.set(tags)
        return lead
