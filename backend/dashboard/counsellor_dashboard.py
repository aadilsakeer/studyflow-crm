from django.db.models import Count, Q
from django.utils import timezone

from admissions.models import Application, Student
from leads.models import Lead


class CounsellorDashboardService:

    @staticmethod
    def empty():
        return {
            'my_pipeline': 0,
            'qualified_leads': 0,
            'profile_evaluation': 0,
            'university_selection': 0,
            'application_ready': 0,
            'students_created': 0,
            'applications': 0,
            'metrics': {
                'conversion_rate': 0,
                'readiness_rate': 0,
            },
        }

    @staticmethod
    def get_dashboard(company, user, range_key='30d'):
        if not company or not user:
            return CounsellorDashboardService.empty()

        from dashboard.analytics import (
            get_period_bounds,
            normalize_range,
        )

        range_key = normalize_range(range_key)
        start, end, _, _ = get_period_bounds(range_key)

        lead_qs = Lead.objects.filter(
            company=company,
            is_deleted=False,
            assigned_counsellor=user,
        )

        pipeline_statuses = (
            'qualified',
            'counsellor_assigned',
            'profile_evaluation',
            'university_selection',
            'application_ready',
        )

        my_pipeline = lead_qs.filter(
            status__in=pipeline_statuses,
        ).count()

        stage_counts = lead_qs.filter(
            status__in=pipeline_statuses,
        ).values('status').annotate(
            total=Count('id'),
        )
        counts = {row['status']: row['total'] for row in stage_counts}

        students_qs = Student.objects.filter(
            company=company,
            is_deleted=False,
            assigned_counselor=user,
        )

        if start and end:
            students_created = students_qs.filter(
                created_at__gte=start,
                created_at__lt=end,
            ).count()
            assigned_in_range = lead_qs.filter(
                counsellor_assigned_at__gte=start,
                counsellor_assigned_at__lt=end,
            ).count()
        else:
            students_created = students_qs.count()
            assigned_in_range = lead_qs.filter(
                counsellor_assigned_at__isnull=False,
            ).count()

        applications = Application.objects.filter(
            student__company=company,
            student__assigned_counselor=user,
            is_deleted=False,
        ).count()

        ready_count = lead_qs.filter(
            status='application_ready',
        ).count()
        conversion_rate = 0

        if assigned_in_range > 0:
            conversion_rate = round(
                (students_created / assigned_in_range) * 100,
                2,
            )

        readiness_rate = 0

        if my_pipeline > 0:
            readiness_rate = round(
                (ready_count / my_pipeline) * 100,
                2,
            )

        return {
            'my_pipeline': my_pipeline,
            'qualified_leads': counts.get('qualified', 0),
            'profile_evaluation': counts.get(
                'profile_evaluation',
                0,
            ),
            'university_selection': counts.get(
                'university_selection',
                0,
            ),
            'application_ready': ready_count,
            'students_created': students_created,
            'applications': applications,
            'metrics': {
                'conversion_rate': conversion_rate,
                'readiness_rate': readiness_rate,
            },
            'range': range_key,
        }
