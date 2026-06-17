from rest_framework import serializers


class DashboardSerializer(
    serializers.Serializer
):

    total_leads = serializers.IntegerField()

    total_students = serializers.IntegerField()

    total_applications = serializers.IntegerField()

    total_candidates = serializers.IntegerField()

    total_employees = serializers.IntegerField()

    total_work_visa_cases = serializers.IntegerField()

    total_revenue = serializers.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    todays_follow_ups = serializers.IntegerField()

    pending_follow_ups = serializers.IntegerField()

    completed_today = serializers.IntegerField()