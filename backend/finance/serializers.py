from rest_framework import serializers

from core.validators import (
    get_request_company,
    validate_application_in_company,
    validate_payment_in_company,
    validate_student_in_company,
)

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

    def validate_student(self, student):
        validate_student_in_company(
            student,
            get_request_company(self.context),
        )
        return student

    def validate_application(self, application):
        if not application:
            return application

        validate_application_in_company(
            application,
            get_request_company(self.context),
        )
        return application


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

    def validate_student(self, student):
        validate_student_in_company(
            student,
            get_request_company(self.context),
        )
        return student

    def validate_payment(self, payment):
        validate_payment_in_company(
            payment,
            get_request_company(self.context),
        )
        return payment


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

    def validate_payment(self, payment):
        validate_payment_in_company(
            payment,
            get_request_company(self.context),
        )
        return payment


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

    def validate_payment(self, payment):
        validate_payment_in_company(
            payment,
            get_request_company(self.context),
        )
        return payment


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
