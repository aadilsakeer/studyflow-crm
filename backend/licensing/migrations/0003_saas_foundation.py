import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def populate_plan_codes(apps, schema_editor):
    Plan = apps.get_model('licensing', 'SubscriptionPlan')
    for plan in Plan.objects.all():
        base = slugify(plan.name).replace('-', '_') or f'plan_{plan.pk}'
        code = base
        suffix = 1
        while Plan.objects.filter(code=code).exclude(pk=plan.pk).exists():
            code = f'{base}_{suffix}'
            suffix += 1
        plan.code = code
        plan.save(update_fields=['code'])


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_task_company'),
        ('licensing', '0002_subscriptionplan_companysubscription_companymodule'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='code',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.RunPython(populate_plan_codes, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='subscriptionplan',
            name='code',
            field=models.CharField(max_length=50, unique=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_leads',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_students',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_storage_mb',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_users',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='max_whatsapp_per_month',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='razorpay_plan_monthly_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='razorpay_plan_yearly_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='sort_order',
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='stripe_price_monthly_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='stripe_price_yearly_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='trial_days',
            field=models.PositiveIntegerField(default=14),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='auto_renew',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='billing_cycle',
            field=models.CharField(default='monthly', max_length=10),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='cancelled_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='current_period_end',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='current_period_start',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='razorpay_customer_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='razorpay_subscription_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='status',
            field=models.CharField(default='trial', max_length=20),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='stripe_customer_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='stripe_subscription_id',
            field=models.CharField(blank=True, max_length=120),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='trial_ends_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='companysubscription',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='companysubscription',
            name='plan',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                to='licensing.subscriptionplan',
            ),
        ),
        migrations.CreateModel(
            name='CompanySettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('timezone', models.CharField(default='Asia/Kolkata', max_length=64)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('billing_email', models.EmailField(blank=True, max_length=254)),
                ('brand_name', models.CharField(blank=True, max_length=255)),
                ('brand_primary_color', models.CharField(default='#2563EB', max_length=7)),
                ('onboarding_step', models.PositiveSmallIntegerField(default=0)),
                ('onboarding_completed_at', models.DateTimeField(blank=True, null=True)),
                ('storage_used_mb', models.PositiveIntegerField(default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('company', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='settings', to='core.company')),
            ],
        ),
        migrations.CreateModel(
            name='PlanModule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='licensing.module')),
                ('plan', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='licensing.subscriptionplan')),
            ],
            options={'unique_together': {('plan', 'module')}},
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='modules',
            field=models.ManyToManyField(blank=True, related_name='plans', through='licensing.PlanModule', to='licensing.module'),
        ),
        migrations.CreateModel(
            name='BillingInvoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('invoice_number', models.CharField(max_length=32, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('status', models.CharField(default='draft', max_length=20)),
                ('period_start', models.DateField(blank=True, null=True)),
                ('period_end', models.DateField(blank=True, null=True)),
                ('due_date', models.DateField(blank=True, null=True)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('stripe_invoice_id', models.CharField(blank=True, max_length=120)),
                ('razorpay_invoice_id', models.CharField(blank=True, max_length=120)),
                ('line_items', models.JSONField(blank=True, default=list)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_invoices', to='core.company')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='invoices', to='licensing.companysubscription')),
            ],
            options={'ordering': ['-created_at']},
        ),
        migrations.CreateModel(
            name='BillingPayment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.DecimalField(decimal_places=2, max_digits=12)),
                ('currency', models.CharField(default='INR', max_length=3)),
                ('status', models.CharField(default='pending', max_length=20)),
                ('provider', models.CharField(default='manual', max_length=20)),
                ('provider_payment_id', models.CharField(blank=True, max_length=120)),
                ('provider_checkout_id', models.CharField(blank=True, max_length=120)),
                ('paid_at', models.DateTimeField(blank=True, null=True)),
                ('metadata', models.JSONField(blank=True, default=dict)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('company', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='billing_payments', to='core.company')),
                ('invoice', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='licensing.billinginvoice')),
                ('subscription', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='payments', to='licensing.companysubscription')),
            ],
            options={'ordering': ['-created_at']},
        ),
    ]
