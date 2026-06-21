from django.db import migrations, models
import django.db.models.deletion


STATUS_MAP = {
    'contacted': 'called',
    'follow_up': 'follow_up',
    'lost': 'not_interested',
}


def migrate_lead_statuses(apps, schema_editor):
    Lead = apps.get_model('leads', 'Lead')

    for old, new in STATUS_MAP.items():
        Lead.objects.filter(status=old).update(status=new)


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0010_soft_delete'),
    ]

    operations = [
        migrations.AddField(
            model_name='lead',
            name='assigned_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='lead',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_leads',
                to='accounts.customuser',
            ),
        ),
        migrations.RunPython(
            migrate_lead_statuses,
            migrations.RunPython.noop,
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
                    ('counsellor_assigned', 'Counsellor Assigned'),
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
                    'assigned_to',
                    'is_deleted',
                    'status',
                ],
                name='lead_co_assign_status_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='calllog',
            index=models.Index(
                fields=['called_by', '-call_time'],
                name='calllog_user_time_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='followup',
            index=models.Index(
                fields=[
                    'assigned_to',
                    'completed',
                    'follow_up_date',
                ],
                name='followup_user_status_date_idx',
            ),
        ),
        migrations.AlterField(
            model_name='calllog',
            name='call_time',
            field=models.DateTimeField(
                auto_now_add=True,
                db_index=True,
            ),
        ),
    ]
