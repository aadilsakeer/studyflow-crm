from rest_framework import serializers


class ReportSummarySerializer(serializers.Serializer):

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