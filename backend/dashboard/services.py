from django.utils import timezone

from leads.models import FollowUp, LeadTimeline

from recruitment.models import (
    Candidate,
)

from workvisa.models import (
    WorkVisaCase,
)

from accounts.models import (
    CustomUser,
)

from .analytics import DashboardAnalyticsService


class DashboardService:

    @staticmethod
    def empty_dashboard():
        empty = (
            DashboardAnalyticsService.empty_analytics()
        )
        return {
            **empty,
            "total_candidates": 0,
            "total_employees": 0,
            "total_work_visa_cases": 0,
            "todays_follow_ups": 0,
            "pending_follow_ups": 0,
            "completed_today": 0,
            "recent_activities": [],
        }

    @staticmethod
    def get_dashboard_data(
        company,
        range_key='30d',
    ):
        if not company:
            return DashboardService.empty_dashboard()

        analytics = (
            DashboardAnalyticsService.get_analytics(
                company,
                range_key,
            )
        )

        today = timezone.localdate()

        follow_ups = FollowUp.objects.filter(
            lead__company=company,
            lead__is_deleted=False,
        )

        data = {
            **analytics,
            'total_candidates':
                Candidate.objects.filter(
                    company=company,
                ).count(),
            'total_employees':
                CustomUser.objects.filter(
                    company=company,
                ).count(),
            'total_work_visa_cases':
                WorkVisaCase.objects.filter(
                    company=company,
                ).count(),
            'todays_follow_ups':
                follow_ups.filter(
                    follow_up_date__date=today,
                    completed=False,
                ).count(),
            'pending_follow_ups':
                follow_ups.filter(
                    completed=False,
                ).count(),
            'completed_today':
                follow_ups.filter(
                    completed=True,
                    completed_at__date=today,
                ).count(),
            'recent_activities':
                DashboardService.get_recent_activities(
                    company,
                ),
        }

        return data

    @staticmethod
    def get_recent_activities(company, limit=10):
        timelines = LeadTimeline.objects.filter(
            lead__company=company,
            lead__is_deleted=False,
        ).select_related(
            "lead",
            "performed_by",
        ).order_by(
            "-created_at",
        )[:limit]

        activities = []

        for item in timelines:
            performed_by = None

            if item.performed_by:
                performed_by = (
                    item.performed_by.get_full_name()
                    or item.performed_by.username
                )

            activities.append({
                "id": item.id,
                "action": item.action,
                "description": item.description,
                "lead_name": (
                    f"{item.lead.first_name} "
                    f"{item.lead.last_name}".strip()
                ),
                "performed_by": performed_by,
                "created_at": item.created_at.isoformat(),
            })

        return activities
