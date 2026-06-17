from rest_framework import serializers
from .models import Lead


class LeadSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lead
        fields = "__all__"
        read_only_fields = (
            "created_at",
            "updated_at",
            "company",
            "score",
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

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        lead = Lead.objects.create(**validated_data)
        if tags:
            lead.tags.set(tags)
        return lead
