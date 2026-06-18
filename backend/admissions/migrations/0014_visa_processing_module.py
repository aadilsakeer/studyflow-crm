# Generated manually for visa processing module upgrade

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


STATUS_MAP = {
    'not_started': 'draft',
    'preparing': 'draft',
    'submitted': 'submitted',
    'biometrics_completed': 'biometrics',
    'approved': 'approved',
    'rejected': 'rejected',
}


def populate_visa_case_fields(apps, schema_editor):
    VisaCase = apps.get_model('admissions', 'VisaCase')

    for visa in VisaCase.objects.select_related(
        'application__student',
    ).iterator():
        application = visa.application
        student = application.student

        visa.company_id = student.company_id
        visa.student_id = student.id
        visa.country = student.destination_country or 'Unknown'
        visa.visa_type = 'student'
        visa.status = STATUS_MAP.get(
            visa.status,
            'draft',
        )

        visa.save(
            update_fields=[
                'company_id',
                'student_id',
                'country',
                'visa_type',
                'status',
            ],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0013_offer_letter_module'),
        ('core', '0003_task_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='visacase',
            old_name='biometrics_date',
            new_name='appointment_date',
        ),
        migrations.RenameField(
            model_name='visacase',
            old_name='remarks',
            new_name='notes',
        ),
        migrations.AddField(
            model_name='visacase',
            name='company',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='student',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='visa_cases',
                to='admissions.student',
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='country',
            field=models.CharField(
                default='Unknown',
                max_length=100,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='visacase',
            name='visa_type',
            field=models.CharField(
                choices=[
                    ('student', 'Student Visa'),
                    ('dependent', 'Dependent Visa'),
                    ('short_term', 'Short Term'),
                    ('other', 'Other'),
                ],
                default='student',
                max_length=30,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='visa_number',
            field=models.CharField(
                blank=True,
                max_length=100,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='application_date',
            field=models.DateField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='is_deleted',
            field=models.BooleanField(
                db_index=True,
                default=False,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='deleted_at',
            field=models.DateTimeField(
                blank=True,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='updated_at',
            field=models.DateTimeField(
                auto_now=True,
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='offer_letter',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='visa_cases',
                to='admissions.offerletter',
            ),
        ),
        migrations.AlterField(
            model_name='visacase',
            name='application',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='visa_cases',
                to='admissions.application',
            ),
        ),
        migrations.AlterField(
            model_name='visacase',
            name='status',
            field=models.CharField(
                choices=[
                    ('draft', 'Draft'),
                    ('submitted', 'Submitted'),
                    ('biometrics', 'Biometrics'),
                    ('processing', 'Processing'),
                    ('approved', 'Approved'),
                    ('rejected', 'Rejected'),
                ],
                default='draft',
                max_length=20,
            ),
        ),
        migrations.RunPython(
            populate_visa_case_fields,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='visacase',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AlterField(
            model_name='visacase',
            name='student',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='visa_cases',
                to='admissions.student',
            ),
        ),
        migrations.AddField(
            model_name='visacase',
            name='student_documents',
            field=models.ManyToManyField(
                blank=True,
                related_name='visa_cases',
                to='admissions.studentdocument',
            ),
        ),
        migrations.AddIndex(
            model_name='visacase',
            index=models.Index(
                fields=['company', '-created_at'],
                name='visa_company_created_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='visacase',
            index=models.Index(
                fields=['student', 'status'],
                name='visa_student_status_idx',
            ),
        ),
    ]
