from datetime import date

from django.utils import timezone

from leads.models import Lead, FollowUp, LeadTimeline

from admissions.models import (
    Student,
    Application,
)

from recruitment.models import (
    Candidate,
)

from workvisa.models import (
    WorkVisaCase,
)

from finance.models import (
    Payment,
)

from accounts.models import (
    CustomUser,
)


class DashboardService:

    @staticmethod
    def empty_dashboard():
        return {
            "total_leads": 0,
            "total_students": 0,
            "total_applications": 0,
            "total_candidates": 0,
            "total_employees": 0,
            "total_work_visa_cases": 0,
            "total_revenue": 0,
            "todays_follow_ups": 0,
            "pending_follow_ups": 0,
            "completed_today": 0,
            "lead_trend": DashboardService._empty_trend(),
            "recent_activities": [],
        }

    @staticmethod
    def _empty_trend():
        today = timezone.localdate()
        trend = []

        for i in range(5, -1, -1):
            year = today.year
            month = today.month - i

            while month <= 0:
                month += 12
                year -= 1

            trend.append({
                "month": date(
                    year,
                    month,
                    1,
                ).strftime("%b"),
                "leads": 0,
            })

        return trend

    @staticmethod
    def get_lead_trend(company):
        today = timezone.localdate()
        trend = []

        for i in range(5, -1, -1):
            year = today.year
            month = today.month - i

            while month <= 0:
                month += 12
                year -= 1

            count = Lead.objects.filter(
                company=company,
                created_at__year=year,
                created_at__month=month,
            ).count()

            trend.append({
                "month": date(
                    year,
                    month,
                    1,
                ).strftime("%b"),
                "leads": count,
            })

        return trend

    @staticmethod
    def get_recent_activities(company, limit=10):
        timelines = LeadTimeline.objects.filter(
            lead__company=company,
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

    @staticmethod
    def get_dashboard_data(
        company,
    ):
        if not company:
            return DashboardService.empty_dashboard()

        revenue = Payment.objects.filter(
            company=company,
            status='paid'
        ).values_list(
            'amount',
            flat=True
        )

        today = timezone.localdate()

        follow_ups = FollowUp.objects.filter(
            lead__company=company
        )

        return {

            'total_leads':
                Lead.objects.filter(
                    company=company
                ).count(),

            'total_students':
                Student.objects.filter(
                    company=company
                ).count(),

            'total_applications':
                Application.objects.filter(
                    student__company=company
                ).count(),

            'total_candidates':
                Candidate.objects.filter(
                    company=company
                ).count(),

            'total_employees':
                CustomUser.objects.filter(
                    company=company
                ).count(),

            'total_work_visa_cases':
                WorkVisaCase.objects.filter(
                    company=company
                ).count(),

            'total_revenue':
                sum(revenue) if revenue else 0,

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

            'lead_trend':
                DashboardService.get_lead_trend(
                    company,
                ),

            'recent_activities':
                DashboardService.get_recent_activities(
                    company,
                ),
        }
