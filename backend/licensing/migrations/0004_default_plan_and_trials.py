from datetime import timedelta

from django.db import migrations
from django.utils import timezone


def seed_default_plan_and_trials(apps, schema_editor):
    Plan = apps.get_model('licensing', 'SubscriptionPlan')
    Company = apps.get_model('core', 'Company')
    Subscription = apps.get_model('licensing', 'CompanySubscription')
    Settings = apps.get_model('licensing', 'CompanySettings')

    plan, _ = Plan.objects.get_or_create(
        code='starter',
        defaults={
            'name': 'Starter',
            'monthly_price': 4999,
            'yearly_price': 49999,
            'trial_days': 14,
            'max_users': 50,
            'max_leads': 5000,
            'max_students': 1000,
            'max_whatsapp_per_month': 2000,
            'max_storage_mb': 10240,
            'sort_order': 1,
            'is_active': True,
        },
    )

    now = timezone.now()
    trial_end = now + timedelta(days=plan.trial_days)

    for company in Company.objects.all():
        Settings.objects.get_or_create(
            company=company,
            defaults={'billing_email': company.email or ''},
        )
        Subscription.objects.get_or_create(
            company=company,
            defaults={
                'plan': plan,
                'status': 'trial',
                'billing_cycle': 'monthly',
                'start_date': now.date(),
                'trial_ends_at': trial_end,
                'current_period_start': now,
                'current_period_end': trial_end,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('licensing', '0003_saas_foundation'),
        ('core', '0003_task_company'),
    ]

    operations = [
        migrations.RunPython(
            seed_default_plan_and_trials,
            migrations.RunPython.noop,
        ),
    ]
