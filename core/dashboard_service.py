from datetime import date

from leads.models import Lead

from admissions.models import (
    Student,
    Application,
    Document,
    VisaCase,
    OfferLetter,
)

from finance.models import (
    Payment,
)

from core.models import (
    Task,
)

from accounts.models import (
    CustomUser,
)

from hrm.models import (
    Attendance,
    LeaveRequest,
    Resignation,
)


class DashboardService:

    @staticmethod
    def get_stats():

        total_revenue = (
            Payment.objects.filter(
                status='paid'
            )
            .values_list('amount', flat=True)
        )

        return {

            # CRM

            "total_leads": Lead.objects.count(),

            # Admissions

            "students": Student.objects.count(),

            "applications": Application.objects.count(),

            "documents": Document.objects.count(),

            "offer_letters": OfferLetter.objects.count(),

            "visa_cases": VisaCase.objects.count(),

            "pending_documents": Document.objects.filter(
                status='pending'
            ).count(),

            "pending_visas": VisaCase.objects.exclude(
                status='approved'
            ).count(),

            # Finance

            "total_revenue": sum(total_revenue) if total_revenue else 0,

            "pending_payments": Payment.objects.filter(
                status='pending'
            ).count(),

            # Tasks

            "pending_tasks": Task.objects.exclude(
                status='completed'
            ).count(),

            # HR

            "employees": CustomUser.objects.count(),

            "present_today": Attendance.objects.filter(
                attendance_date=date.today(),
                status='present'
            ).count(),

            "leaves_today": LeaveRequest.objects.filter(
                status='approved'
            ).count(),

            "resignations": Resignation.objects.count(),
        }