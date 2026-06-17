from rest_framework import serializers

from .models import (
    Payment,
    Invoice,
    Receipt,
    Refund,
    Expense
)


class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payment
        fields = (
            "id",
            "company",
            "student",
            "application",
            "payment_type",
            "amount",
            "payment_date",
            "reference_number",
            "status",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = (
            "id",
            "invoice_number",
            "student",
            "payment",
            "invoice_date",
            "due_date",
            "amount",
            "status",
            "created_at",
        )
        read_only_fields = (
            "invoice_number",
            "created_at",
        )


class ReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = (
            "id",
            "receipt_number",
            "payment",
            "receipt_date",
            "amount",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "receipt_number",
            "created_at",
        )


class RefundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Refund
        fields = (
            "id",
            "payment",
            "amount",
            "reason",
            "status",
            "refund_date",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = (
            "id",
            "company",
            "title",
            "category",
            "amount",
            "expense_date",
            "remarks",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )
