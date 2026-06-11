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
        fields = '__all__'


class InvoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Invoice
        fields = '__all__'


class ReceiptSerializer(serializers.ModelSerializer):

    class Meta:
        model = Receipt
        fields = '__all__'


class RefundSerializer(serializers.ModelSerializer):

    class Meta:
        model = Refund
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Expense
        fields = '__all__'