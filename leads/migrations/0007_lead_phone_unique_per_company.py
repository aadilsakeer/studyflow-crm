from django.db import migrations, models


class Migration(migrations.Migration):

    atomic = False

    dependencies = [
        ("leads", "0006_leadimportlog"),
    ]

    operations = [
        migrations.AlterField(
            model_name="lead",
            name="phone",
            field=models.CharField(
                db_index=True,
                max_length=20,
            ),
        ),
        migrations.AddConstraint(
            model_name="lead",
            constraint=models.UniqueConstraint(
                fields=("company", "phone"),
                name="unique_lead_phone_per_company",
            ),
        ),
    ]
