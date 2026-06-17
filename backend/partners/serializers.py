from rest_framework import serializers

from .models import (
    PartnerUniversity,
    PartnerContact,
    PartnerAgreement,
    PartnerCommission
)


class PartnerUniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerUniversity
        fields = (
            "id",
            "company",
            "name",
            "country",
            "website",
            "is_active",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class PartnerContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerContact
        fields = (
            "id",
            "university",
            "name",
            "designation",
            "email",
            "phone",
        )


class PartnerAgreementSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerAgreement
        fields = (
            "id",
            "university",
            "agreement_date",
            "expiry_date",
            "status",
            "notes",
        )


class PartnerCommissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerCommission
        fields = (
            "id",
            "university",
            "course_level",
            "commission_percentage",
            "notes",
        )
