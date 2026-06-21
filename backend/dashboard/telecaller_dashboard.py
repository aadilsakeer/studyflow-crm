from django.db.models import Q
from django.utils import timezone

from leads.models import CallLog, FollowUp, Lead


class TelecallerDashboardService:

    @staticmethod
    def empty():
        return {
            'my_leads': 0,
            'todays_calls': 0,
            'pending_follow_ups': 0,
            'interested_leads': 0,
            'documents_requested': 0,
            'documents_received': 0,
            'converted_leads': 0,
            'metrics': {
                'calls_made': 0,
                'followups_completed': 0,
                'interested_leads': 0,
                'conversion_rate': 0,
            },
        }

    @staticmethod
    def get_dashboard(company, user, range_key='30d'):
        if not company or not user:
            return TelecallerDashboardService.empty()

        from dashboard.analytics import (
            get_period_bounds,
            normalize_range,
        )

        range_key = normalize_range(range_key)
        start, end, _, _ = get_period_bounds(range_key)

        today = timezone.localdate()

        lead_qs = Lead.objects.filter(
            company=company,
            is_deleted=False,
            assigned_to=user,
        )

        call_qs = CallLog.objects.filter(
            called_by=user,
            lead__company=company,
            lead__is_deleted=False,
        )

        followup_qs = FollowUp.objects.filter(
            assigned_to=user,
            lead__company=company,
            lead__is_deleted=False,
        )

        my_leads = lead_qs.exclude(
            status__in=('converted', 'not_interested'),
        ).count()

        todays_calls = call_qs.filter(
            call_time__date=today,
        ).count()

        pending_follow_ups = followup_qs.filter(
            completed=False,
        ).count()

        interested_leads = lead_qs.filter(
            status='interested',
        ).count()

        documents_requested = lead_qs.filter(
            status='documents_requested',
        ).count()

        documents_received = lead_qs.filter(
            status='documents_received',
        ).count()

        converted_leads = lead_qs.filter(
            status='converted',
        ).count()

        if start and end:
            calls_made = call_qs.filter(
                call_time__gte=start,
                call_time__lt=end,
            ).count()

            followups_completed = followup_qs.filter(
                completed=True,
                completed_at__gte=start,
                completed_at__lt=end,
            ).count()

            interested_in_range = lead_qs.filter(
                status='interested',
                updated_at__gte=start,
                updated_at__lt=end,
            ).count()

            assigned_in_range = lead_qs.filter(
                assigned_at__gte=start,
                assigned_at__lt=end,
            ).count()

            converted_in_range = lead_qs.filter(
                status='converted',
                updated_at__gte=start,
                updated_at__lt=end,
            ).count()
        else:
            calls_made = call_qs.count()
            followups_completed = followup_qs.filter(
                completed=True,
            ).count()
            interested_in_range = lead_qs.filter(
                status='interested',
            ).count()
            assigned_in_range = lead_qs.filter(
                assigned_at__isnull=False,
            ).count()
            converted_in_range = converted_leads

        conversion_rate = 0

        if assigned_in_range > 0:
            conversion_rate = round(
                (converted_in_range / assigned_in_range) * 100,
                2,
            )

        return {
            'my_leads': my_leads,
            'todays_calls': todays_calls,
            'pending_follow_ups': pending_follow_ups,
            'interested_leads': interested_leads,
            'documents_requested': documents_requested,
            'documents_received': documents_received,
            'converted_leads': converted_leads,
            'metrics': {
                'calls_made': calls_made,
                'followups_completed': followups_completed,
                'interested_leads': interested_in_range,
                'conversion_rate': conversion_rate,
            },
            'range': range_key,
        }
