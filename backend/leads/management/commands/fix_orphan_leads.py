from django.core.management.base import BaseCommand

from core.models import Company
from leads.models import Lead


class Command(BaseCommand):

    help = (
        "Assign leads with no company to the "
        "first company in the database."
    )

    def handle(self, *args, **options):
        company = Company.objects.order_by(
            "id",
        ).first()

        if not company:
            self.stdout.write(
                self.style.WARNING(
                    "No company found. "
                    "Create a company first."
                )
            )
            return

        updated = Lead.objects.filter(
            company__isnull=True,
        ).update(company=company)

        self.stdout.write(
            self.style.SUCCESS(
                f"Assigned {updated} orphan lead(s) "
                f"to {company}."
            )
        )
