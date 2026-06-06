from django.db.models import Q

from .models import Lead


class LeadSearchService:

    @staticmethod
    def search(query):

        return Lead.objects.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(email__icontains=query)
        ).distinct()