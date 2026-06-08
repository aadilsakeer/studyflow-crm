from django.contrib import admin

from .models import (
    Payment,
    Invoice,
    Receipt
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'student',
        'payment_type',
        'amount',
        'status',
        'payment_date'
    )

    list_filter = (
        'status',
        'payment_type'
    )

    search_fields = (
        'student__student_id',
        'reference_number'
    )


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):

    list_display = (
        'invoice_number',
        'student',
        'amount',
        'invoice_date',
        'status'
    )

    list_filter = (
        'status',
    )

    search_fields = (
        'invoice_number',
        'student__student_id'
    )


@admin.register(Receipt)
class ReceiptAdmin(admin.ModelAdmin):

    list_display = (
        'receipt_number',
        'payment',
        'amount',
        'receipt_date'
    )

    search_fields = (
        'receipt_number',
    )