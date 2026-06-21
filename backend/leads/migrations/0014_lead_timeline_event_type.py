from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0013_counsellor_pipeline'),
    ]

    operations = [
        migrations.AddField(
            model_name='leadtimeline',
            name='event_type',
            field=models.CharField(
                blank=True,
                db_index=True,
                default='',
                max_length=50,
            ),
        ),
        migrations.AddIndex(
            model_name='leadtimeline',
            index=models.Index(
                fields=['lead', 'event_type', '-created_at'],
                name='timeline_lead_event_idx',
            ),
        ),
    ]
