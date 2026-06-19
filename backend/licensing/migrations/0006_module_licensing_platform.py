import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licensing', '0005_phase83_support_branding'),
    ]

    operations = [
        migrations.AddField(
            model_name='companymodule',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='companymodule',
            name='expires_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companymodule',
            name='from_plan',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='companymodule',
            name='is_trial',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='companymodule',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='companymodule',
            name='usage_limits',
            field=models.JSONField(blank=True, default=dict),
        ),
    ]
