from django.core.management.base import BaseCommand

from core.operations import run_db_backup, test_restore_readiness, verify_latest_backup


class Command(BaseCommand):
    help = 'Create PostgreSQL/database backup'

    def handle(self, *args, **options):
        result = run_db_backup()
        self.stdout.write(self.style.SUCCESS(f"Backup: {result['path']} ({result['size']} bytes)"))
