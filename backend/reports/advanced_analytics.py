from decimal import Decimal

from django.db.models import Count, Q, Sum
from django.db.models.functions import Coalesce, TruncMonth

from admissions.models import Application, OfferLetter, Student, VisaCase
from dashboard.analytics import (
    RANGE_LABELS,
    get_period_bounds,
    normalize_range,
)
from finance.models import Payment
from leads.models import CallLog, Lead


def _in_range(qs, field, start, end):
    if start is None or end is None:
        return qs

    return qs.filter(
        **{
            f'{field}__gte': start,
            f'{field}__lt': end,
        },
    )


def _user_label(user):
    if not user:
        return 'Unassigned'

    return user.get_full_name() or user.username


def _rows_to_chart(rows, label_key, value_key='value'):
    return [
        {
            'label': row[label_key],
            value_key: row[value_key],
        }
        for row in rows
    ]


class AdvancedReportService:

    @staticmethod
    def get_reports(company, range_key='30d'):
        range_key = normalize_range(range_key)
        current_start, current_end, _, _ = get_period_bounds(
            range_key,
        )

        lead_qs = _in_range(
            Lead.objects.filter(
                company=company,
                is_deleted=False,
            ),
            'created_at',
            current_start,
            current_end,
        )

        student_qs = _in_range(
            Student.objects.filter(
                company=company,
                is_deleted=False,
            ),
            'created_at',
            current_start,
            current_end,
        )

        offer_qs = _in_range(
            OfferLetter.objects.filter(
                company=company,
                is_deleted=False,
            ),
            'created_at',
            current_start,
            current_end,
        )

        visa_qs = _in_range(
            VisaCase.objects.filter(
                company=company,
                is_deleted=False,
            ),
            'created_at',
            current_start,
            current_end,
        )

        payment_qs = _in_range(
            Payment.objects.filter(
                company=company,
                status='paid',
            ),
            'created_at',
            current_start,
            current_end,
        )

        lead_source_roi = []
        source_rows = lead_qs.values(
            'source__name',
        ).annotate(
            leads=Count('id'),
            converted=Count(
                'id',
                filter=Q(status='converted'),
            ),
        ).order_by('-leads')

        for row in source_rows:
            source_name = row['source__name'] or 'Unknown'
            leads_count = row['leads']
            converted = row['converted']
            revenue = payment_qs.filter(
                student__lead__source__name=row['source__name'],
            ).aggregate(
                total=Coalesce(Sum('amount'), Decimal('0')),
            )['total']

            lead_source_roi.append({
                'source': source_name,
                'leads': leads_count,
                'converted': converted,
                'conversion_rate': round(
                    (converted / leads_count) * 100,
                    1,
                ) if leads_count else 0,
                'revenue': float(revenue or 0),
            })

        telecaller_rows = lead_qs.values(
            'assigned_to__id',
            'assigned_to__first_name',
            'assigned_to__last_name',
            'assigned_to__username',
        ).annotate(
            leads=Count('id'),
            converted=Count(
                'id',
                filter=Q(status='converted'),
            ),
        ).order_by('-leads')

        telecaller_performance = []
        telecaller_ids = [
            row['assigned_to__id']
            for row in telecaller_rows
            if row['assigned_to__id']
        ]

        call_counts = {
            row['called_by_id']: row['total']
            for row in CallLog.objects.filter(
                lead__company=company,
                called_by_id__in=telecaller_ids,
            ).values('called_by_id').annotate(
                total=Count('id'),
            )
        }

        for row in telecaller_rows:
            user_id = row['assigned_to__id']

            if not user_id:
                continue

            leads_count = row['leads']
            converted = row['converted']

            telecaller_performance.append({
                'staff_id': user_id,
                'name': (
                    f"{row['assigned_to__first_name']} "
                    f"{row['assigned_to__last_name']}".strip()
                    or row['assigned_to__username']
                ),
                'leads': leads_count,
                'calls': call_counts.get(user_id, 0),
                'converted': converted,
                'conversion_rate': round(
                    (converted / leads_count) * 100,
                    1,
                ) if leads_count else 0,
            })

        counsellor_rows = lead_qs.exclude(
            assigned_counsellor__isnull=True,
        ).values(
            'assigned_counsellor__id',
            'assigned_counsellor__first_name',
            'assigned_counsellor__last_name',
            'assigned_counsellor__username',
        ).annotate(
            leads=Count('id'),
            converted=Count(
                'id',
                filter=Q(status='converted'),
            ),
        ).order_by('-converted')

        counsellor_performance = [
            {
                'staff_id': row['assigned_counsellor__id'],
                'name': (
                    f"{row['assigned_counsellor__first_name']} "
                    f"{row['assigned_counsellor__last_name']}".strip()
                    or row['assigned_counsellor__username']
                ),
                'leads': row['leads'],
                'converted': row['converted'],
                'conversion_rate': round(
                    (row['converted'] / row['leads']) * 100,
                    1,
                ) if row['leads'] else 0,
            }
            for row in counsellor_rows
        ]

        country_rows = student_qs.exclude(
            destination_country='',
        ).values(
            'destination_country',
        ).annotate(
            students=Count('id'),
        ).order_by('-students')

        country_performance = [
            {
                'country': row['destination_country'],
                'students': row['students'],
            }
            for row in country_rows
        ]

        application_qs = Application.objects.filter(
            student__company=company,
            student__is_deleted=False,
            is_deleted=False,
        )

        if current_start and current_end:
            application_qs = application_qs.filter(
                created_at__gte=current_start,
                created_at__lt=current_end,
            )

        application_count = application_qs.count()

        university_rows = application_qs.values(
            'university_name',
        ).annotate(
            applications=Count('id'),
        ).order_by('-applications')

        university_performance = [
            {
                'university': row['university_name'],
                'applications': row['applications'],
            }
            for row in university_rows
        ]

        offers_received = offer_qs.count()
        offers_accepted = offer_qs.filter(
            status='accepted',
        ).count()

        offer_conversion = {
            'offers_received': offers_received,
            'offers_accepted': offers_accepted,
            'conversion_rate': round(
                (offers_accepted / offers_received) * 100,
                1,
            ) if offers_received else 0,
        }

        visas_submitted = visa_qs.exclude(
            status='draft',
        ).count()
        visas_approved = visa_qs.filter(
            status='approved',
        ).count()

        visa_success = {
            'visas_submitted': visas_submitted,
            'visas_approved': visas_approved,
            'success_rate': round(
                (visas_approved / visas_submitted) * 100,
                1,
            ) if visas_submitted else 0,
        }

        revenue_total = payment_qs.aggregate(
            total=Coalesce(Sum('amount'), Decimal('0')),
        )['total']

        revenue = {
            'total_revenue': float(revenue_total or 0),
            'payment_count': payment_qs.count(),
        }

        total_leads = lead_qs.count()
        converted_leads = lead_qs.filter(
            status='converted',
        ).count()
        active_students = student_qs.count()

        kpis = {
            'total_leads': total_leads,
            'active_students': active_students,
            'applications': application_count,
            'revenue': float(revenue_total or 0),
            'conversion_rate': round(
                (converted_leads / total_leads) * 100,
                1,
            ) if total_leads else 0,
        }

        funnel = [
            {
                'label': 'New',
                'value': lead_qs.filter(
                    status__in=[
                        'new',
                        'assigned',
                        'called',
                    ],
                ).count(),
            },
            {
                'label': 'Interested',
                'value': lead_qs.filter(
                    status__in=[
                        'interested',
                        'follow_up',
                    ],
                ).count(),
            },
            {
                'label': 'Qualified',
                'value': lead_qs.filter(
                    status__in=[
                        'qualified',
                        'documents_requested',
                        'documents_received',
                        'counsellor_assigned',
                        'profile_evaluation',
                        'university_selection',
                        'application_ready',
                    ],
                ).count(),
            },
            {
                'label': 'Student',
                'value': converted_leads,
            },
        ]

        monthly_rows = (
            lead_qs.annotate(
                month=TruncMonth('created_at'),
            )
            .values('month')
            .annotate(
                leads=Count('id'),
                converted=Count(
                    'id',
                    filter=Q(status='converted'),
                ),
            )
            .order_by('month')
        )

        monthly_trends = [
            {
                'label': (
                    row['month'].strftime('%b %Y')
                    if row['month'] else 'Unknown'
                ),
                'leads': row['leads'],
                'converted': row['converted'],
            }
            for row in monthly_rows
        ]

        recent_conversions = [
            {
                'name': (
                    f"{row['first_name']} {row['last_name']}".strip()
                ),
                'phone': row['phone'],
                'converted_at': row['updated_at'],
            }
            for row in lead_qs.filter(
                status='converted',
            ).order_by('-updated_at')[:10].values(
                'first_name',
                'last_name',
                'phone',
                'updated_at',
            )
        ]

        return {
            'range': range_key,
            'range_label': RANGE_LABELS.get(range_key, range_key),
            'kpis': kpis,
            'funnel': funnel,
            'monthly_trends': monthly_trends,
            'recent_conversions': recent_conversions,
            'lead_source_roi': lead_source_roi,
            'telecaller_performance': telecaller_performance,
            'counsellor_performance': counsellor_performance,
            'country_performance': country_performance,
            'university_performance': university_performance,
            'offer_conversion': offer_conversion,
            'visa_success': visa_success,
            'revenue': revenue,
            'charts': {
                'lead_source': _rows_to_chart(
                    lead_source_roi,
                    'source',
                    'leads',
                ),
                'country': _rows_to_chart(
                    country_performance,
                    'country',
                    'students',
                ),
                'telecaller': _rows_to_chart(
                    telecaller_performance,
                    'name',
                    'converted',
                ),
                'revenue': _rows_to_chart(
                    lead_source_roi,
                    'source',
                    'revenue',
                ),
            },
        }
