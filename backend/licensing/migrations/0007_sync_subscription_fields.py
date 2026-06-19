import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('licensing', '0006_module_licensing_platform'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='subscriptionplan',
            options={'ordering': ['sort_order', 'name']},
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='billing_cycle',
            field=models.CharField(
                choices=[('monthly', 'Monthly'), ('yearly', 'Yearly')],
                default='monthly',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='company',
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='subscription',
                to='core.company',
            ),
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='created_at',
            field=models.DateTimeField(
                auto_now_add=True,
                default=django.utils.timezone.now,
            ),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='status',
            field=models.CharField(
                choices=[
                    ('trial', 'Trial'),
                    ('active', 'Active'),
                    ('past_due', 'Past_due'),
                    ('cancelled', 'Cancelled'),
                    ('expired', 'Expired'),
                ],
                default='trial',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
    ]
