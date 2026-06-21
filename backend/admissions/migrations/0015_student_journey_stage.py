from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0014_visa_processing_module'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='journey_stage',
            field=models.CharField(
                blank=True,
                default='',
                max_length=30,
            ),
        ),
    ]
