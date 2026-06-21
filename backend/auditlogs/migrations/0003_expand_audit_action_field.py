from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlogs', '0002_auditlog_company_created_idx'),
    ]

    operations = [
        migrations.AlterField(
            model_name='auditlog',
            name='action',
            field=models.CharField(max_length=50),
        ),
    ]
