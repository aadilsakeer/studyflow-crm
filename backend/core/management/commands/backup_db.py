from django.core.management.base import BaseCommand, CommandError

from core.operations import run_db_backup
from core.pg_dump import PgDumpNotFoundError


class Command(BaseCommand):
    help = 'Create PostgreSQL/database backup'

    def handle(self, *args, **options):
        try:
            result = run_db_backup()
        except PgDumpNotFoundError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f"Backup: {result['path']} ({result['size']} bytes)",
        ))
