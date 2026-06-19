from django.db import models
from django.utils import timezone

from core.models import Company

from .constants import (
    BILLING_CYCLES,
    INVOICE_STATUS_DRAFT,
    PAYMENT_STATUS_PENDING,
    PROVIDER_MANUAL,
    SUBSCRIPTION_STATUS_TRIAL,
    SUBSCRIPTION_STATUSES,
)


class Module(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class SubscriptionPlan(models.Model):

    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=50, unique=True)
    monthly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    yearly_price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
    )
    description = models.TextField(blank=True)
    trial_days = models.PositiveIntegerField(default=14)
    max_users = models.PositiveIntegerField(null=True, blank=True)
    max_leads = models.PositiveIntegerField(null=True, blank=True)
    max_students = models.PositiveIntegerField(null=True, blank=True)
    max_whatsapp_per_month = models.PositiveIntegerField(
        null=True,
        blank=True,
    )
    max_storage_mb = models.PositiveIntegerField(null=True, blank=True)
    stripe_price_monthly_id = models.CharField(max_length=120, blank=True)
    stripe_price_yearly_id = models.CharField(max_length=120, blank=True)
    razorpay_plan_monthly_id = models.CharField(max_length=120, blank=True)
    razorpay_plan_yearly_id = models.CharField(max_length=120, blank=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveSmallIntegerField(default=0)

    modules = models.ManyToManyField(
        Module,
        through='PlanModule',
        related_name='plans',
        blank=True,
    )

    class Meta:
        ordering = ['sort_order', 'name']

    def __str__(self):
        return self.name


class PlanModule(models.Model):

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE,
    )
    module = models.ForeignKey(
        Module,
        on_delete=models.CASCADE,
    )

    class Meta:
        unique_together = ('plan', 'module')

    def __str__(self):
        return f'{self.plan} + {self.module}'


class CompanySettings(models.Model):

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='settings',
    )
    timezone = models.CharField(max_length=64, default='Asia/Kolkata')
    currency = models.CharField(max_length=3, default='INR')
    billing_email = models.EmailField(blank=True)
    brand_name = models.CharField(max_length=255, blank=True)
    brand_primary_color = models.CharField(
        max_length=7,
        default='#2563EB',
    )
    brand_logo = models.ImageField(
        upload_to='branding/logos/',
        null=True,
        blank=True,
    )
    brand_favicon = models.ImageField(
        upload_to='branding/favicons/',
        null=True,
        blank=True,
    )
    onboarding_step = models.PositiveSmallIntegerField(default=0)
    onboarding_completed_at = models.DateTimeField(null=True, blank=True)
    storage_used_mb = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Settings: {self.company}'


class CompanySubscription(models.Model):

    company = models.OneToOneField(
        Company,
        on_delete=models.CASCADE,
        related_name='subscription',
    )
    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.PROTECT,
    )
    status = models.CharField(
        max_length=20,
        choices=[(s, s.title()) for s in SUBSCRIPTION_STATUSES],
        default=SUBSCRIPTION_STATUS_TRIAL,
    )
    billing_cycle = models.CharField(
        max_length=10,
        choices=[(c, c.title()) for c in BILLING_CYCLES],
        default='monthly',
    )
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    trial_ends_at = models.DateTimeField(null=True, blank=True)
    current_period_start = models.DateTimeField(null=True, blank=True)
    current_period_end = models.DateTimeField(null=True, blank=True)
    stripe_customer_id = models.CharField(max_length=120, blank=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True)
    razorpay_customer_id = models.CharField(max_length=120, blank=True)
    razorpay_subscription_id = models.CharField(max_length=120, blank=True)
    auto_renew = models.BooleanField(default=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def is_usable(self):
        if not self.is_active:
            return False

        if self.status in ('active', 'past_due'):
            return True

        if self.status == SUBSCRIPTION_STATUS_TRIAL:
            if not self.trial_ends_at:
                return True
            return timezone.now() <= self.trial_ends_at

        return False

    def __str__(self):
        return f'{self.company} - {self.plan}'


class CompanyModule(models.Model):

    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    is_enabled = models.BooleanField(default=True)
    is_trial = models.BooleanField(default=False)
    expires_at = models.DateTimeField(null=True, blank=True)
    usage_limits = models.JSONField(default=dict, blank=True)
    from_plan = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('company', 'module')

    def is_accessible(self):
        if not self.is_enabled:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True

    def __str__(self):
        return f'{self.company} - {self.module}'


class BillingInvoice(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='billing_invoices',
    )
    subscription = models.ForeignKey(
        CompanySubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
    )
    invoice_number = models.CharField(max_length=32, unique=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(
        max_length=20,
        default=INVOICE_STATUS_DRAFT,
    )
    period_start = models.DateField(null=True, blank=True)
    period_end = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    stripe_invoice_id = models.CharField(max_length=120, blank=True)
    razorpay_invoice_id = models.CharField(max_length=120, blank=True)
    line_items = models.JSONField(default=list, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.invoice_number


class BillingPayment(models.Model):

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='billing_payments',
    )
    invoice = models.ForeignKey(
        BillingInvoice,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    subscription = models.ForeignKey(
        CompanySubscription,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='payments',
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='INR')
    status = models.CharField(max_length=20, default=PAYMENT_STATUS_PENDING)
    provider = models.CharField(max_length=20, default=PROVIDER_MANUAL)
    provider_payment_id = models.CharField(max_length=120, blank=True)
    provider_checkout_id = models.CharField(max_length=120, blank=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.provider} {self.amount} {self.status}'


class TenantSupportTicket(models.Model):

    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_WAITING = 'waiting'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    SLA_ON_TRACK = 'on_track'
    SLA_AT_RISK = 'at_risk'
    SLA_BREACHED = 'breached'

    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name='support_tickets',
    )
    created_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_support_tickets',
    )
    assigned_to = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_support_tickets',
    )
    subject = models.CharField(max_length=255)
    description = models.TextField()
    status = models.CharField(max_length=20, default=STATUS_OPEN)
    priority = models.CharField(max_length=20, default=PRIORITY_NORMAL)
    sla_due_at = models.DateTimeField(null=True, blank=True)
    sla_status = models.CharField(max_length=20, default=SLA_ON_TRACK)
    resolved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.company} - {self.subject}'


class TenantSupportMessage(models.Model):

    ticket = models.ForeignKey(
        TenantSupportTicket,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    author = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    body = models.TextField()
    is_internal = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message on {self.ticket_id}'


class TenantSupportAttachment(models.Model):

    ticket = models.ForeignKey(
        TenantSupportTicket,
        on_delete=models.CASCADE,
        related_name='attachments',
    )
    message = models.ForeignKey(
        TenantSupportMessage,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='attachments',
    )
    file = models.FileField(upload_to='support/attachments/')
    filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename
