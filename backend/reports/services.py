from leads.models import Lead

from admissions.models import (
    Student,
    Application,
    VisaCase,
)

from finance.models import (
    Payment,
    Expense,
    Refund
)

from hrm.models import (
    Attendance,
)

from recruitment.models import (
    Candidate,
    Interview,
    Deployment
)

from workvisa.models import (
    WorkVisaCase,
)

from accounts.models import CustomUser
from core.models import Task


class ReportService:

    @staticmethod
    def get_summary(company):

        revenue = (
            Payment.objects.filter(
                company=company,
                status='paid'
            )
            .values_list(
                'amount',
                flat=True
            )
        )

        return {

            "total_leads":
                Lead.objects.filter(
                    company=company
                ).count(),

            "total_students":
                Student.objects.filter(
                    company=company
                ).count(),

            "total_applications":
                Application.objects.filter(
                    student__company=company
                ).count(),

            "total_visa_cases":
                VisaCase.objects.filter(
                    application__student__company=company
                ).count(),

            "total_work_visa_cases":
                WorkVisaCase.objects.filter(
                    company=company
                ).count(),

            "total_candidates":
                Candidate.objects.filter(
                    company=company
                ).count(),

            "total_attendance_records":
                Attendance.objects.filter(
                    company=company
                ).count(),

            "total_revenue":
                sum(revenue) if revenue else 0,
        }


class FinanceReportService:

    @staticmethod
    def get_finance_summary(company):

        paid_amounts = Payment.objects.filter(
            company=company,
            status='paid'
        ).values_list(
            'amount',
            flat=True
        )

        expense_amounts = Expense.objects.filter(
            company=company
        ).values_list(
            'amount',
            flat=True
        )

        refund_amounts = Refund.objects.filter(
            payment__company=company
        ).values_list(
            'amount',
            flat=True
        )

        return {

            "total_revenue":
                sum(paid_amounts) if paid_amounts else 0,

            "total_payments":
                Payment.objects.filter(
                    company=company
                ).count(),

            "pending_payments":
                Payment.objects.filter(
                    company=company
                ).exclude(
                    status='paid'
                ).count(),

            "total_expenses":
                sum(expense_amounts) if expense_amounts else 0,

            "total_refunds":
                sum(refund_amounts) if refund_amounts else 0,
        }


class LeadConversionReportService:

    @staticmethod
    def get_conversion_summary(company):

        total_leads = Lead.objects.filter(
            company=company
        ).count()

        total_students = Student.objects.filter(
            company=company
        ).count()

        total_applications = Application.objects.filter(
            student__company=company
        ).count()

        visa_approved = VisaCase.objects.filter(
            application__student__company=company,
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


class StaffPerformanceReportService:

    @staticmethod
    def get_staff_summary(company):

        return {

            "total_staff":
                CustomUser.objects.filter(
                    company=company
                ).count(),

            "attendance_records":
                Attendance.objects.filter(
                    company=company
                ).count(),

            "pending_tasks":
                Task.objects.filter(
                    company=company,
                    status='pending'
                ).count(),

            "completed_tasks":
                Task.objects.filter(
                    company=company,
                    status='completed'
                ).count(),
        }


class CountryAnalyticsService:

    @staticmethod
    def get_country_summary(company):

        country_data = {}

        students = Student.objects.filter(
            company=company
        ).exclude(
            destination_country=''
        )

        for student in students:

            country = student.destination_country

            if country not in country_data:
                country_data[country] = 0

            country_data[country] += 1

        return country_data


class RecruitmentAnalyticsService:

    @staticmethod
    def get_recruitment_summary(company):

        return {

            "total_candidates":
                Candidate.objects.filter(
                    company=company
                ).count(),

            "total_interviews":
                Interview.objects.filter(
                    candidate__company=company
                ).count(),

            "selected_candidates":
                Interview.objects.filter(
                    candidate__company=company,
                    status='selected'
                ).count(),

            "deployed_candidates":
                Deployment.objects.filter(
                    candidate__company=company
                ).count(),
        }


class WorkVisaAnalyticsService:

    @staticmethod
    def get_work_visa_summary(company):

        return {

            "total_cases":
                WorkVisaCase.objects.filter(
                    company=company
                ).count(),

            "approved_cases":
                WorkVisaCase.objects.filter(
                    company=company,
                    status='approved'
                ).count(),

            "rejected_cases":
                WorkVisaCase.objects.filter(
                    company=company,
                    status='rejected'
                ).count(),

            "pending_cases":
                WorkVisaCase.objects.filter(
                    company=company
                ).exclude(
                    status__in=[
                        'approved',
                        'rejected'
                    ]
                ).count(),
        }