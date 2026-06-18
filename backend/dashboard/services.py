from django.utils import timezone

from activity.models import StudentTimeline
from core.task_service import get_task_summary
from leads.models import FollowUp, LeadTimeline

class DashboardService:

    @staticmethod
    def empty_dashboard():
        from .analytics import DashboardAnalyticsService

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
            "todays_tasks": 0,
            "pending_tasks": 0,
            "overdue_tasks": 0,
            "completed_today_tasks": 0,
            "due_reminders": 0,
        }

    @staticmethod
    def get_dashboard_data(
        company,
        range_key='30d',
        user=None,
    ):
        from accounts.models import CustomUser
        from recruitment.models import Candidate
        from workvisa.models import WorkVisaCase

        from .analytics import DashboardAnalyticsService

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
            **get_task_summary(company, user),
        }

        return data

    @staticmethod
    def get_recent_activities(company, limit=10):
        lead_items = LeadTimeline.objects.filter(
            lead__company=company,
            lead__is_deleted=False,
        ).select_related(
            "lead",
            "performed_by",
        ).order_by(
            "-created_at",
        )[:limit]

        student_items = StudentTimeline.objects.filter(
            student__company=company,
            student__is_deleted=False,
        ).select_related(
            "student",
            "performed_by",
        ).order_by(
            "-created_at",
        )[:limit]

        activities = []

        for item in lead_items:
            performed_by = None

            if item.performed_by:
                performed_by = (
                    item.performed_by.get_full_name()
                    or item.performed_by.username
                )

            activities.append({
                "id": f"lead-{item.id}",
                "entity_type": "lead",
                "entity_id": item.lead_id,
                "event_type": item.event_type,
                "action": item.action,
                "description": item.description,
                "entity_name": (
                    f"{item.lead.first_name} "
                    f"{item.lead.last_name}".strip()
                ),
                "performed_by": performed_by,
                "created_at": item.created_at.isoformat(),
            })

        for item in student_items:
            performed_by = None

            if item.performed_by:
                performed_by = (
                    item.performed_by.get_full_name()
                    or item.performed_by.username
                )

            activities.append({
                "id": f"student-{item.id}",
                "entity_type": "student",
                "entity_id": item.student_id,
                "event_type": item.event_type,
                "action": item.action,
                "description": item.description,
                "entity_name": item.student.student_id,
                "performed_by": performed_by,
                "created_at": item.created_at.isoformat(),
            })

        activities.sort(
            key=lambda row: row["created_at"],
            reverse=True,
        )

        return activities[:limit]
