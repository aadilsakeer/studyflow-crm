import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0012_lead_import_engine'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='application_readiness',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='lead',
            name='assigned_counsellor',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='counsellor_leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='counsellor_assigned_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='profile_evaluation_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='qualified_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='lead',
            name='qualified_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='qualified_leads',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='lead',
            name='recommended_countries',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='lead',
            name='recommended_universities',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AlterField(
            model_name='lead',
            name='status',
            field=models.CharField(
                choices=[
                    ('new', 'New'),
                    ('assigned', 'Assigned'),
                    ('called', 'Called'),
                    ('interested', 'Interested'),
                    ('not_interested', 'Not Interested'),
                    ('follow_up', 'Follow-up'),
                    ('documents_requested', 'Documents Requested'),
                    ('documents_received', 'Documents Received'),
                    ('qualified', 'Qualified'),
                    ('counsellor_assigned', 'Counsellor Assigned'),
                    ('profile_evaluation', 'Profile Evaluation'),
                    ('university_selection', 'University Selection'),
                    ('application_ready', 'Application Ready'),
                    ('converted', 'Converted'),
                ],
                default='new',
                max_length=30,
            ),
        ),
        migrations.AddIndex(
            model_name='lead',
            index=models.Index(
                fields=[
                    'company',
                    'assigned_counsellor',
                    'is_deleted',
                    'status',
                ],
                name='lead_co_couns_status_idx',
            ),
        ),
    ]
