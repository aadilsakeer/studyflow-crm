from django.core.management.base import BaseCommand

from licensing.models import Module, SubscriptionPlan


class Command(BaseCommand):

    help = "Seed licensing modules and subscription plans"

    def handle(self, *args, **options):

        modules = [
            ("CRM", "crm"),
            ("Admissions", "admissions"),
            ("Recruitment", "recruitment"),
            ("Work Visa", "workvisa"),
            ("Finance", "finance"),
            ("HRM", "hrm"),
            ("Reports", "reports"),
            ("Knowledge Base", "knowledgebase"),
            ("Client Portal", "clientportal"),
            ("Notifications", "notifications"),
            ('Dashboard', 'dashboard'),
            ('Client Portal', 'clientportal'),
            ('WhatsApp', 'whatsapp'),
        ]

        for name, code in modules:
            Module.objects.get_or_create(
                name=name,
                code=code
            )

        SubscriptionPlan.objects.get_or_create(
            name="Basic",
            defaults={
                "monthly_price": 4999,
                "yearly_price": 49999,
            }
        )

        SubscriptionPlan.objects.get_or_create(
            name="Professional",
            defaults={
                "monthly_price": 9999,
                "yearly_price": 99999,
            }
        )

        SubscriptionPlan.objects.get_or_create(
            name="Enterprise",
            defaults={
                "monthly_price": 19999,
                "yearly_price": 199999,
            }
        )

        self.stdout.write(
            self.style.SUCCESS(
                "Licensing data seeded successfully."
            )
        )