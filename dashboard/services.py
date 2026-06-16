from leads.models import Lead

from admissions.models import (
    Student,
    Application
)

from recruitment.models import (
    Candidate
)

from workvisa.models import (
    WorkVisaCase
)

from finance.models import (
    Payment
)

from accounts.models import (
    CustomUser
)


class DashboardService:

    @staticmethod
    def get_dashboard_data(
        company
    ):

        revenue = Payment.objects.filter(
            company=company,
            status='paid'
        ).values_list(
            'amount',
            flat=True
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
        }