from rest_framework import serializers

from .models import (
    WorkVisaCase,
    WorkVisaDocument,
    WorkVisaTimeline
)


class WorkVisaCaseSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaCase
        fields = (
            "id",
            "company",
            "candidate",
            "assigned_staff",
            "destination_country",
            "visa_type",
            "status",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class WorkVisaDocumentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaDocument
        fields = (
            "id",
            "visa_case",
            "document_name",
            "status",
            "remarks",
        )


class WorkVisaTimelineSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaTimeline
        fields = (
            "id",
            "visa_case",
            "title",
            "description",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )
