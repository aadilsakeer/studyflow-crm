import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('auditlogs', '0001_initial'),
        ('admissions', '0015_student_journey_stage'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('activity', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='StudentTimeline',
            fields=[
                ('id', models.BigAutoField(
                    auto_created=True,
                    primary_key=True,
                    serialize=False,
                    verbose_name='ID',
                )),
                ('event_type', models.CharField(
                    db_index=True,
                    max_length=50,
                )),
                ('action', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('audit_log', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to='auditlogs.auditlog',
                )),
                ('performed_by', models.ForeignKey(
                    blank=True,
                    null=True,
                    on_delete=django.db.models.deletion.SET_NULL,
                    to=settings.AUTH_USER_MODEL,
                )),
                ('student', models.ForeignKey(
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='timeline_events',
                    to='admissions.student',
                )),
            ],
            options={
                'indexes': [
                    models.Index(
                        fields=['student', '-created_at'],
                        name='student_timeline_created_idx',
                    ),
                    models.Index(
                        fields=['student', 'event_type', '-created_at'],
                        name='student_timeline_event_idx',
                    ),
                ],
            },
        ),
    ]
