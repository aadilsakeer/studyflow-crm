from rest_framework import serializers

from .models import (
    Report,
    ReportSchedule
)


class ReportSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = Report
        fields = (
            "id",
            "company",
            "title",
            "report_type",
            "generated_by",
            "file",
            "status",
            "created_at",
        )
        read_only_fields = (
            "company",
            "generated_by",
            "created_at",
        )


class ReportScheduleSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ReportSchedule
        fields = (
            "id",
            "company",
            "report_type",
            "frequency",
            "email_to",
            "is_active",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class ReportSummarySerializer(
    serializers.Serializer
):

    total_leads = serializers.IntegerField()

    total_students = serializers.IntegerField()

    total_applications = serializers.IntegerField()

    total_visa_cases = serializers.IntegerField()

    total_work_visa_cases = serializers.IntegerField()

    total_candidates = serializers.IntegerField()

    total_attendance_records = serializers.IntegerField()

    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )
