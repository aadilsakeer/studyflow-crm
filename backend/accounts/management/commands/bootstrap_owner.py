from django.core.management import call_command
from django.core.management.base import BaseCommand

from accounts.constants import ROLE_ADMIN
from accounts.models import CustomUser, Role


OWNER_USERNAME = 'owner'
OWNER_EMAIL = 'owner@globvio.local'
OWNER_PASSWORD = 'Owner@123'


class Command(BaseCommand):
    help = 'Create or reset the platform owner superuser account.'

    def handle(self, *args, **options):
        call_command('seed_rbac')

        user, created = CustomUser.objects.update_or_create(
            username=OWNER_USERNAME,
            defaults={
                'email': OWNER_EMAIL,
                'is_superuser': True,
                'is_staff': True,
                'is_active': True,
                'first_name': 'Platform',
                'last_name': 'Owner',
            },
        )
        user.set_password(OWNER_PASSWORD)
        admin_role = Role.objects.filter(name=ROLE_ADMIN).first()
        if admin_role:
            user.role = admin_role
        user.save()

        action = 'Created' if created else 'Reset'
        self.stdout.write(self.style.SUCCESS(f'{action} platform owner account.'))
        self.stdout.write('')
        self.stdout.write('Owner credentials:')
        self.stdout.write(f'  Username: {OWNER_USERNAME}')
        self.stdout.write(f'  Email:    {OWNER_EMAIL}')
        self.stdout.write(f'  Password: {OWNER_PASSWORD}')
        self.stdout.write('')
        self.stdout.write('Login at the main app URL, then open /owner')
        self.stdout.write('Or run: python manage.py bootstrap_owner  (to reset password)')
