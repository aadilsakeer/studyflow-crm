from django.core.management.base import BaseCommand

from core.operations import test_restore_readiness, verify_latest_backup


class Command(BaseCommand):
    help = 'Verify latest backup and dry-run restore readiness'

    def handle(self, *args, **options):
        v = verify_latest_backup()
        r = test_restore_readiness()
        if v.get('ok') and r.get('ok'):
            self.stdout.write(self.style.SUCCESS(f"OK: {v['file']}"))
        else:
            self.stdout.write(self.style.ERROR(str(v if not v.get('ok') else r)))
