from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlogs', '0001_initial'),
    ]

    operations = [
        migrations.AddIndex(
            model_name='auditlog',
            index=models.Index(
                fields=['company', '-created_at'],
                name='audit_company_created_idx',
            ),
        ),
    ]
