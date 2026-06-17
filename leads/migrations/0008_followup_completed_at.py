from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("leads", "0007_lead_phone_unique_per_company"),
    ]

    operations = [
        migrations.AddField(
            model_name="followup",
            name="completed_at",
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
    ]
