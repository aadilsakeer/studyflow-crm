from django.contrib import admin

from .models import (
    BillingInvoice,
    BillingPayment,
    CompanyModule,
    CompanySettings,
    CompanySubscription,
    Module,
    PlanModule,
    SubscriptionPlan,
    TenantSupportAttachment,
    TenantSupportMessage,
    TenantSupportTicket,
)


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'code', 'monthly_price', 'trial_days',
        'max_users', 'max_leads', 'is_active',
    )


@admin.register(CompanySubscription)
class CompanySubscriptionAdmin(admin.ModelAdmin):
    list_display = ('company', 'plan', 'status', 'trial_ends_at', 'is_active')
    list_filter = ('status',)


@admin.register(CompanySettings)
class CompanySettingsAdmin(admin.ModelAdmin):
    list_display = ('company', 'onboarding_step', 'billing_email')


@admin.register(BillingInvoice)
class BillingInvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'company', 'amount', 'status', 'created_at')


@admin.register(BillingPayment)
class BillingPaymentAdmin(admin.ModelAdmin):
    list_display = ('company', 'provider', 'amount', 'status', 'created_at')


@admin.register(TenantSupportTicket)
class TenantSupportTicketAdmin(admin.ModelAdmin):
    list_display = ('subject', 'company', 'status', 'priority', 'sla_status', 'created_at')
    list_filter = ('status', 'priority', 'sla_status')
