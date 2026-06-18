import calendar
from datetime import timedelta
from decimal import Decimal

from django.db.models import (
    Count,
    Q,
    Sum,
)
from django.db.models.functions import (
    TruncDay,
    TruncHour,
    TruncMonth,
    TruncWeek,
)
from django.utils import timezone

from admissions.models import (
    Application,
    OfferLetter,
    Student,
    VisaCase,
)
from finance.models import Payment
from leads.models import Lead


VALID_RANGES = (
    'today',
    '7d',
    '30d',
    '90d',
    '6m',
    '12m',
    'all',
)

QUALIFIED_LEAD_STATUSES = (
    'contacted',
    'interested',
    'follow_up',
    'converted',
)

RANGE_LABELS = {
    'today': 'Today',
    '7d': 'Last 7 Days',
    '30d': 'Last 30 Days',
    '90d': 'Last 90 Days',
    '6m': 'Last 6 Months',
    '12m': 'Last 12 Months',
    'all': 'All Time',
}


def normalize_range(range_key):
    if range_key in VALID_RANGES:
        return range_key
    return '30d'


def _start_of_day(dt):
    local = timezone.localtime(dt)
    return local.replace(
        hour=0,
        minute=0,
        second=0,
        microsecond=0,
    )


def _add_months(dt, months):
    month_index = (
        dt.year * 12 + (dt.month - 1) + months
    )
    year = month_index // 12
    month = month_index % 12 + 1
    day = min(
        dt.day,
        calendar.monthrange(year, month)[1],
    )
    return dt.replace(
        year=year,
        month=month,
        day=day,
    )


def get_period_bounds(range_key):
    now = timezone.now()
    today = _start_of_day(now)
    tomorrow = today + timedelta(days=1)

    if range_key == 'all':
        compare_start = _add_months(today, -24)
        compare_mid = _add_months(today, -12)
        return None, None, compare_start, compare_mid

    if range_key == 'today':
        current_start = today
        current_end = tomorrow
    elif range_key == '7d':
        current_start = today - timedelta(days=6)
        current_end = tomorrow
    elif range_key == '30d':
        current_start = today - timedelta(days=29)
        current_end = tomorrow
    elif range_key == '90d':
        current_start = today - timedelta(days=89)
        current_end = tomorrow
    elif range_key == '6m':
        current_start = _add_months(today, -6)
        current_end = tomorrow
    elif range_key == '12m':
        current_start = _add_months(today, -12)
        current_end = tomorrow
    else:
        current_start = today - timedelta(days=29)
        current_end = tomorrow

    duration = current_end - current_start
    previous_end = current_start
    previous_start = previous_end - duration

    return (
        current_start,
        current_end,
        previous_start,
        previous_end,
    )


def _get_trunc_fn(range_key):
    if range_key == 'today':
        return TruncHour
    if range_key in ('7d', '30d'):
        return TruncDay
    if range_key == '90d':
        return TruncWeek
    return TruncMonth


def _format_bucket(value, range_key):
    if not value:
        return ''

    local = timezone.localtime(value)

    if range_key == 'today':
        return local.strftime('%I %p')
    if range_key in ('7d', '30d', '90d'):
        return local.strftime('%d %b')
    return local.strftime('%b %Y')


def _apply_period(qs, field, start, end):
    if start is None and end is None:
        return qs

    filters = {}

    if start is not None:
        filters[f'{field}__gte'] = start

    if end is not None:
        filters[f'{field}__lt'] = end

    return qs.filter(**filters)


def _growth_pct(current, previous):
    current = current or 0
    previous = previous or 0

    if previous:
        return round(
            (current - previous) / previous * 100,
            2,
        )

    if current:
        return 100.0

    return 0.0


def _kpi(current, previous):
    return {
        'value': current,
        'previous': previous,
        'growth_pct': _growth_pct(
            current,
            previous,
        ),
    }


def _aggregate_count(qs, field, start, end):
    return _apply_period(
        qs,
        field,
        start,
        end,
    ).count()


def _aggregate_sum(qs, field, start, end, sum_field):
    result = _apply_period(
        qs,
        field,
        start,
        end,
    ).aggregate(total=Sum(sum_field))

    total = result['total']

    if total is None:
        return 0

    if isinstance(total, Decimal):
        return float(total)

    return total


def _build_count_trend(
    qs,
    field,
    start,
    end,
    range_key,
):
    trunc = _get_trunc_fn(range_key)
    rows = (
        _apply_period(qs, field, start, end)
        .annotate(bucket=trunc(field))
        .values('bucket')
        .annotate(value=Count('id'))
        .order_by('bucket')
    )

    return [
        {
            'label': _format_bucket(
                row['bucket'],
                range_key,
            ),
            'value': row['value'],
        }
        for row in rows
    ]


def _build_sum_trend(
    qs,
    field,
    start,
    end,
    range_key,
    sum_field,
):
    trunc = _get_trunc_fn(range_key)
    rows = (
        _apply_period(qs, field, start, end)
        .annotate(bucket=trunc(field))
        .values('bucket')
        .annotate(
            value=Sum(sum_field),
        )
        .order_by('bucket')
    )

    return [
        {
            'label': _format_bucket(
                row['bucket'],
                range_key,
            ),
            'value': float(row['value'] or 0),
        }
        for row in rows
    ]


class DashboardAnalyticsService:

    @staticmethod
    def get_analytics(company, range_key='30d'):
        range_key = normalize_range(range_key)

        if not company:
            return DashboardAnalyticsService.empty_analytics(
                range_key,
            )

        (
            current_start,
            current_end,
            previous_start,
            previous_end,
        ) = get_period_bounds(range_key)

        lead_qs = Lead.objects.filter(
            company=company,
            is_deleted=False,
        )
        qualified_qs = lead_qs.filter(
            status__in=QUALIFIED_LEAD_STATUSES,
        )
        student_qs = Student.objects.filter(
            company=company,
            is_deleted=False,
        )
        application_qs = Application.objects.filter(
            student__company=company,
            is_deleted=False,
        )
        offer_qs = OfferLetter.objects.filter(
            application__student__company=company,
            application__student__is_deleted=False,
        )
        visa_qs = VisaCase.objects.filter(
            company=company,
            is_deleted=False,
            status='approved',
        )
        payment_qs = Payment.objects.filter(
            company=company,
            status='paid',
        )

        if range_key == 'all':
            total_leads = lead_qs.count()
            qualified_leads = qualified_qs.count()
            students = student_qs.count()
            applications = application_qs.count()
            offer_letters = offer_qs.count()
            visa_approvals = visa_qs.count()
            revenue = _aggregate_sum(
                payment_qs,
                'created_at',
                None,
                None,
                'amount',
            )

            prev_leads = _aggregate_count(
                lead_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_qualified = _aggregate_count(
                qualified_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_students = _aggregate_count(
                student_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_applications = _aggregate_count(
                application_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_offers = _aggregate_count(
                offer_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_visas = _aggregate_count(
                visa_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_revenue = _aggregate_sum(
                payment_qs,
                'created_at',
                previous_start,
                previous_end,
                'amount',
            )

            trend_start = None
            trend_end = None
        else:
            total_leads = _aggregate_count(
                lead_qs,
                'created_at',
                current_start,
                current_end,
            )
            qualified_leads = _aggregate_count(
                qualified_qs,
                'created_at',
                current_start,
                current_end,
            )
            students = _aggregate_count(
                student_qs,
                'created_at',
                current_start,
                current_end,
            )
            applications = _aggregate_count(
                application_qs,
                'created_at',
                current_start,
                current_end,
            )
            offer_letters = _aggregate_count(
                offer_qs,
                'created_at',
                current_start,
                current_end,
            )
            visa_approvals = _aggregate_count(
                visa_qs,
                'created_at',
                current_start,
                current_end,
            )
            revenue = _aggregate_sum(
                payment_qs,
                'created_at',
                current_start,
                current_end,
                'amount',
            )

            prev_leads = _aggregate_count(
                lead_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_qualified = _aggregate_count(
                qualified_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_students = _aggregate_count(
                student_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_applications = _aggregate_count(
                application_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_offers = _aggregate_count(
                offer_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_visas = _aggregate_count(
                visa_qs,
                'created_at',
                previous_start,
                previous_end,
            )
            prev_revenue = _aggregate_sum(
                payment_qs,
                'created_at',
                previous_start,
                previous_end,
                'amount',
            )

            trend_start = current_start
            trend_end = current_end

        conversion_rate = 0.0
        prev_conversion_rate = 0.0

        if total_leads:
            conversion_rate = round(
                students / total_leads * 100,
                2,
            )

        if prev_leads:
            prev_conversion_rate = round(
                prev_students / prev_leads * 100,
                2,
            )

        trends = {
            'leads': _build_count_trend(
                lead_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
            ),
            'students': _build_count_trend(
                student_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
            ),
            'applications': _build_count_trend(
                application_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
            ),
            'revenue': _build_sum_trend(
                payment_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
                'amount',
            ),
            'offer_letters': _build_count_trend(
                offer_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
            ),
            'visa_approvals': _build_count_trend(
                visa_qs,
                'created_at',
                trend_start,
                trend_end,
                range_key,
            ),
        }

        lead_trend = [
            {
                'month': point['label'],
                'leads': point['value'],
            }
            for point in trends['leads']
        ]

        return {
            'range': range_key,
            'range_label': RANGE_LABELS[range_key],
            'kpis': {
                'total_leads': _kpi(
                    total_leads,
                    prev_leads,
                ),
                'qualified_leads': _kpi(
                    qualified_leads,
                    prev_qualified,
                ),
                'students': _kpi(
                    students,
                    prev_students,
                ),
                'applications': _kpi(
                    applications,
                    prev_applications,
                ),
                'offer_letters': _kpi(
                    offer_letters,
                    prev_offers,
                ),
                'visa_approvals': _kpi(
                    visa_approvals,
                    prev_visas,
                ),
                'conversion_rate': _kpi(
                    conversion_rate,
                    prev_conversion_rate,
                ),
                'revenue': _kpi(
                    revenue,
                    prev_revenue,
                ),
            },
            'trends': trends,
            'lead_trend': lead_trend,
            'total_leads': total_leads,
            'total_students': students,
            'total_applications': applications,
            'total_revenue': revenue,
        }

    @staticmethod
    def empty_analytics(range_key='30d'):
        range_key = normalize_range(range_key)
        zero_kpi = _kpi(0, 0)

        return {
            'range': range_key,
            'range_label': RANGE_LABELS[range_key],
            'kpis': {
                'total_leads': zero_kpi,
                'qualified_leads': zero_kpi,
                'students': zero_kpi,
                'applications': zero_kpi,
                'offer_letters': zero_kpi,
                'visa_approvals': zero_kpi,
                'conversion_rate': zero_kpi,
                'revenue': zero_kpi,
            },
            'trends': {
                'leads': [],
                'students': [],
                'applications': [],
                'revenue': [],
                'offer_letters': [],
                'visa_approvals': [],
            },
            'lead_trend': [],
            'total_leads': 0,
            'total_students': 0,
            'total_applications': 0,
            'total_revenue': 0,
        }
