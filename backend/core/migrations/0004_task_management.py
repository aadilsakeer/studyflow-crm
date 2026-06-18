from django.db import migrations, models
import django.db.models.deletion


def clear_orphan_tasks(apps, schema_editor):
    Task = apps.get_model('core', 'Task')
    Task.objects.filter(company__isnull=True).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0015_student_journey_stage'),
        ('leads', '0014_lead_timeline_event_type'),
        ('core', '0003_task_company'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='task',
            name='lead',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tasks',
                to='leads.lead',
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='task',
            name='reminder_at',
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='student',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='tasks',
                to='admissions.student',
            ),
        ),
        migrations.AddField(
            model_name='task',
            name='task_type',
            field=models.CharField(
                choices=[
                    ('follow_up_call', 'Follow-up Call'),
                    ('document_collection', 'Document Collection'),
                    ('application_submission', 'Application Submission'),
                    ('offer_review', 'Offer Review'),
                    ('visa_appointment', 'Visa Appointment'),
                    ('general_task', 'General Task'),
                ],
                db_index=True,
                default='general_task',
                max_length=40,
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='assigned_to',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='assigned_tasks',
                to='accounts.customuser',
            ),
        ),
        migrations.RunPython(
            clear_orphan_tasks,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='task',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='due_date',
            field=models.DateTimeField(
                blank=True,
                db_index=True,
                null=True,
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='priority',
            field=models.CharField(
                choices=[
                    ('low', 'Low'),
                    ('medium', 'Medium'),
                    ('high', 'High'),
                    ('urgent', 'Urgent'),
                ],
                db_index=True,
                default='medium',
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(
                choices=[
                    ('pending', 'Pending'),
                    ('in_progress', 'In Progress'),
                    ('completed', 'Completed'),
                    ('cancelled', 'Cancelled'),
                ],
                db_index=True,
                default='pending',
                max_length=20,
            ),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(
                fields=['company', 'status', '-due_date'],
                name='task_co_status_due_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(
                fields=['company', 'assigned_to', 'status'],
                name='task_co_assign_status_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(
                fields=['company', 'reminder_at'],
                name='task_co_reminder_idx',
            ),
        ),
    ]
