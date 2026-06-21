from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0003_expense_refund'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='payment',
            index=models.Index(
                fields=['company', 'status', '-created_at'],
                name='pay_company_status_idx',
            ),
        ),
    ]
