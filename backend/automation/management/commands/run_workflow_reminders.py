from django.core.management.base import BaseCommand

from automation.reminder_service import run_all_reminders


class Command(BaseCommand):
    help = 'Run workflow reminder checks and create notifications.'

    def handle(self, *args, **options):
        result = run_all_reminders()

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {result['companies_processed']} companies, "
                f"sent {result['notifications_sent']} notifications.",
            ),
        )
