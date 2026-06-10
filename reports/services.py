from leads.models import Lead

from admissions.models import (
    Student,
    Application,
    VisaCase,
)

from finance.models import (
    Payment,
)

from hrm.models import (
    Attendance,
)

from recruitment.models import (
    Candidate,
)

from workvisa.models import (
    WorkVisaCase,
)


class ReportService:

    @staticmethod
    def get_summary():

        revenue = (
            Payment.objects.filter(
                status='paid'
            )
            .values_list(
                'amount',
                flat=True
            )
        )

        return {

            "total_leads":
                Lead.objects.count(),

            "total_students":
                Student.objects.count(),

            "total_applications":
                Application.objects.count(),

            "total_visa_cases":
                VisaCase.objects.count(),

            "total_work_visa_cases":
                WorkVisaCase.objects.count(),

            "total_candidates":
                Candidate.objects.count(),

            "total_attendance_records":
                Attendance.objects.count(),

            "total_revenue":
                sum(revenue) if revenue else 0,
        }
from finance.models import (
    Payment,
    Expense,
    Refund
)


class FinanceReportService:

    @staticmethod
    def get_finance_summary():

        paid_amounts = Payment.objects.filter(
            status='paid'
        ).values_list(
            'amount',
            flat=True
        )

        expense_amounts = Expense.objects.values_list(
            'amount',
            flat=True
        )

        refund_amounts = Refund.objects.values_list(
            'amount',
            flat=True
        )

        return {

            "total_revenue":
                sum(paid_amounts) if paid_amounts else 0,

            "total_payments":
                Payment.objects.count(),

            "pending_payments":
                Payment.objects.exclude(
                    status='paid'
                ).count(),

            "total_expenses":
                sum(expense_amounts) if expense_amounts else 0,

            "total_refunds":
                sum(refund_amounts) if refund_amounts else 0,
        }
from admissions.models import (
    Student,
    Application,
    VisaCase
)

from leads.models import Lead


class LeadConversionReportService:

    @staticmethod
    def get_conversion_summary():

        total_leads = Lead.objects.count()

        total_students = Student.objects.count()

        total_applications = Application.objects.count()

        visa_approved = VisaCase.objects.filter(
            status='approved'
        ).count()

        lead_to_student_rate = 0

        if total_leads > 0:
            lead_to_student_rate = round(
                (total_students / total_leads) * 100,
                2
            )

        return {
            "total_leads": total_leads,
            "total_students": total_students,
            "total_applications": total_applications,
            "visa_approved": visa_approved,
            "lead_to_student_rate": lead_to_student_rate,
        }
from accounts.models import CustomUser
from hrm.models import Attendance
from core.models import Task


class StaffPerformanceReportService:

    @staticmethod
    def get_staff_summary():

        return {

            "total_staff":
                CustomUser.objects.count(),

            "attendance_records":
                Attendance.objects.count(),

            "pending_tasks":
                Task.objects.filter(
                    status='pending'
                ).count(),

            "completed_tasks":
                Task.objects.filter(
                    status='completed'
                ).count(),
        }
from admissions.models import Student


class CountryAnalyticsService:

    @staticmethod
    def get_country_summary():

        country_data = {}

        students = Student.objects.exclude(
            destination_country=''
        )

        for student in students:

            country = student.destination_country

            if country not in country_data:
                country_data[country] = 0

            country_data[country] += 1

        return country_data

from recruitment.models import (
    Candidate,
    Interview,
    Deployment
)


class RecruitmentAnalyticsService:

    @staticmethod
    def get_recruitment_summary():

        return {

            "total_candidates":
                Candidate.objects.count(),

            "total_interviews":
                Interview.objects.count(),

            "selected_candidates":
                Interview.objects.filter(
                    status='selected'
                ).count(),

            "deployed_candidates":
                Deployment.objects.count(),
        }

from workvisa.models import WorkVisaCase


class WorkVisaAnalyticsService:

    @staticmethod
    def get_work_visa_summary():

        return {

            "total_cases":
                WorkVisaCase.objects.count(),

            "approved_cases":
                WorkVisaCase.objects.filter(
                    status='approved'
                ).count(),

            "rejected_cases":
                WorkVisaCase.objects.filter(
                    status='rejected'
                ).count(),

            "pending_cases":
                WorkVisaCase.objects.exclude(
                    status__in=['approved', 'rejected']
                ).count(),
        }