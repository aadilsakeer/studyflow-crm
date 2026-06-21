import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('leads', '0011_telecaller_assignment'),
        ('core', '0003_task_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='leadimportlog',
            name='assignment_mode',
            field=models.CharField(
                blank=True,
                choices=[
                    ('manual', 'Manual'),
                    ('round_robin', 'Round Robin'),
                    ('even_distribution', 'Even Distribution'),
                ],
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='column_mapping',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='company',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='completed_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='duplicate_rule',
            field=models.CharField(
                choices=[
                    ('phone', 'Phone'),
                    ('email', 'Email'),
                    ('phone_email', 'Phone + Email'),
                ],
                default='phone',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='error_report',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='preview_rows',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='source_columns',
            field=models.JSONField(blank=True, default=list),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='status',
            field=models.CharField(
                choices=[
                    ('uploaded', 'Uploaded'),
                    ('mapped', 'Mapped'),
                    ('validated', 'Validated'),
                    ('completed', 'Completed'),
                    ('failed', 'Failed'),
                ],
                default='uploaded',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='stored_file',
            field=models.FileField(
                blank=True,
                upload_to='lead_imports/',
            ),
        ),
        migrations.AddField(
            model_name='leadimportlog',
            name='telecaller',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lead_imports',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AlterField(
            model_name='leadimportlog',
            name='imported_by',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='lead_import_logs',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddIndex(
            model_name='leadimportlog',
            index=models.Index(
                fields=['company', '-created_at'],
                name='import_company_created_idx',
            ),
        ),
    ]
