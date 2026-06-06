from leads.models import Lead
from admissions.models import (
    Student,
    Application,
    Document,
    VisaCase,
    OfferLetter,
)


class DashboardService:

    @staticmethod
    def get_stats():

        return {
            "total_leads": Lead.objects.count(),

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
        }