import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_task_company'),
        ('hrm', '0004_department_payroll'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Shift',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('start_time', models.TimeField()),
                ('end_time', models.TimeField()),
                ('grace_minutes', models.PositiveSmallIntegerField(default=15)),
                ('is_active', models.BooleanField(default=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='shifts', to='core.company')),
            ],
        ),
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('employee_code', models.CharField(max_length=32)),
                ('full_name', models.CharField(max_length=255)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20)),
                ('designation', models.CharField(blank=True, max_length=120)),
                ('salary_structure', models.JSONField(blank=True, default=dict)),
                ('leave_balance', models.JSONField(blank=True, default=dict)),
                ('joined_at', models.DateField(blank=True, null=True)),
                ('is_active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='hrm_employees', to='core.company')),
                ('department', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='hrm.department')),
                ('reporting_to', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='direct_reports', to='hrm.employee')),
                ('shift', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employees', to='hrm.shift')),
                ('user', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='employee_profile', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['full_name'],
                'unique_together': {('company', 'employee_code')},
            },
        ),
        migrations.CreateModel(
            name='AssetAssignment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('asset_type', models.CharField(choices=[('laptop', 'Laptop'), ('phone', 'Phone'), ('accessory', 'Accessory')], max_length=20)),
                ('asset_name', models.CharField(max_length=255)),
                ('serial_number', models.CharField(blank=True, max_length=120)),
                ('status', models.CharField(default='assigned', max_length=20)),
                ('assigned_at', models.DateTimeField(auto_now_add=True)),
                ('returned_at', models.DateTimeField(blank=True, null=True)),
                ('notes', models.TextField(blank=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_assignments', to='core.company')),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='asset_assignments', to='hrm.employee')),
            ],
            options={'ordering': ['-assigned_at']},
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_in_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_out_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_in_latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_in_longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_out_latitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='check_out_longitude',
            field=models.DecimalField(blank=True, decimal_places=7, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='is_late',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='attendance',
            name='employee_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_records', to='hrm.employee'),
        ),
        migrations.AddField(
            model_name='attendance',
            name='shift',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='attendance_records', to='hrm.shift'),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='leave_type',
            field=models.CharField(default='annual', max_length=50),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='reviewer_notes',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='approved_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='approved_leaves', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='leaverequest',
            name='employee_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='leave_requests', to='hrm.employee'),
        ),
        migrations.AddField(
            model_name='payroll',
            name='salary_structure',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='payroll',
            name='payslip',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='payroll',
            name='payment_status',
            field=models.CharField(default='pending', max_length=20),
        ),
        migrations.AddField(
            model_name='payroll',
            name='paid_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='payroll',
            name='employee_profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payrolls', to='hrm.employee'),
        ),
    ]
