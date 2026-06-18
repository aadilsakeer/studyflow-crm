# Generated manually for offer letter module upgrade

import admissions.models
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def populate_offer_letter_fields(apps, schema_editor):
    OfferLetter = apps.get_model('admissions', 'OfferLetter')

    for offer in OfferLetter.objects.select_related(
        'application__student',
    ).iterator():
        application = offer.application
        student = application.student
        old_status = offer.status

        offer.company_id = student.company_id
        offer.student_id = student.id
        offer.university = application.university_name
        offer.course = application.course_name
        offer.expiry_date = offer.expiry_date

        if old_status in ('conditional', 'unconditional'):
            offer.offer_type = old_status
            offer.status = 'received'
        elif old_status == 'accepted':
            offer.offer_type = 'conditional'
            offer.status = 'accepted'
        elif old_status == 'declined':
            offer.offer_type = 'conditional'
            offer.status = 'rejected'
        else:
            offer.offer_type = 'conditional'
            offer.status = 'received'

        offer.save(
            update_fields=[
                'company_id',
                'student_id',
                'university',
                'course',
                'expiry_date',
                'offer_type',
                'status',
            ],
        )


class Migration(migrations.Migration):

    dependencies = [
        ('admissions', '0012_student_document_verification'),
        ('core', '0003_task_company'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameField(
            model_name='offerletter',
            old_name='acceptance_deadline',
            new_name='expiry_date',
        ),
        migrations.AddField(
            model_name='offerletter',
            name='company',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='student',
            field=models.ForeignKey(
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='offer_letters',
                to='admissions.student',
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='university',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offerletter',
            name='course',
            field=models.CharField(default='', max_length=255),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='offerletter',
            name='offer_type',
            field=models.CharField(
                choices=[
                    ('conditional', 'Conditional'),
                    ('unconditional', 'Unconditional'),
                ],
                default='conditional',
                max_length=20,
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='tuition_fee',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='deposit_amount',
            field=models.DecimalField(
                blank=True,
                decimal_places=2,
                max_digits=12,
                null=True,
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='offer_document',
            field=models.FileField(
                blank=True,
                null=True,
                upload_to=admissions.models.offer_letter_upload_path,
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='original_filename',
            field=models.CharField(blank=True, max_length=255),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='file_size',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='mime_type',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='student_document',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='offer_letters',
                to='admissions.studentdocument',
            ),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='is_deleted',
            field=models.BooleanField(db_index=True, default=False),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='deleted_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='offerletter',
            name='deleted_by',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='+',
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.RunPython(
            populate_offer_letter_fields,
            migrations.RunPython.noop,
        ),
        migrations.AlterField(
            model_name='offerletter',
            name='company',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='core.company',
            ),
        ),
        migrations.AlterField(
            model_name='offerletter',
            name='student',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='offer_letters',
                to='admissions.student',
            ),
        ),
        migrations.AlterField(
            model_name='offerletter',
            name='status',
            field=models.CharField(
                choices=[
                    ('received', 'Received'),
                    ('reviewed', 'Reviewed'),
                    ('accepted', 'Accepted'),
                    ('rejected', 'Rejected'),
                    ('expired', 'Expired'),
                ],
                default='received',
                max_length=20,
            ),
        ),

        migrations.AlterField(
            model_name='offerletter',
            name='offer_number',
            field=models.CharField(max_length=100),
        ),
        migrations.AddIndex(
            model_name='offerletter',
            index=models.Index(
                fields=['company', '-created_at'],
                name='offer_company_created_idx',
            ),
        ),
        migrations.AddIndex(
            model_name='offerletter',
            index=models.Index(
                fields=['student', 'status'],
                name='offer_student_status_idx',
            ),
        ),
        migrations.AddConstraint(
            model_name='offerletter',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_deleted', False)),
                fields=('company', 'offer_number'),
                name='uniq_offer_number_per_company_alive',
            ),
        ),
        migrations.AlterField(
            model_name='studentdocument',
            name='document_type',
            field=models.CharField(
                choices=[
                    ('10th_marksheet', '10th Marksheet'),
                    ('12th_marksheet', '12th Marksheet'),
                    ('degree_certificate', 'Degree Certificate'),
                    ('degree_transcript', 'Degree Transcript'),
                    ('passport', 'Passport'),
                    ('ielts', 'IELTS'),
                    ('pte', 'PTE'),
                    ('sop', 'SOP'),
                    ('lor', 'LOR'),
                    ('resume', 'Resume'),
                    ('university_offer_letter', 'University Offer Letter'),
                    ('bank_statement', 'Bank Statement'),
                    ('sponsor_letter', 'Sponsor Letter'),
                    ('sponsor_id', 'Sponsor ID'),
                    ('income_proof', 'Income Proof'),
                    ('education_loan_letter', 'Education Loan Letter'),
                    ('experience_letter', 'Experience Letter'),
                    ('payslip', 'Payslip'),
                    ('employment_offer_letter', 'Employment Offer Letter'),
                    ('other', 'Other'),
                ],
                max_length=50,
            ),
        ),
    ]
