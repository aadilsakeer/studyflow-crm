from rest_framework import generics

from licensing.decorators import module_required
from auditlogs.services import AuditLogService

from .models import (
    Payment,
    Expense,
    Invoice,
    Receipt,
    Refund
)

from .serializers import (
    PaymentSerializer,
    ExpenseSerializer,
    InvoiceSerializer,
    ReceiptSerializer,
    RefundSerializer
)


class PaymentListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = PaymentSerializer

    def get_queryset(self):

        return Payment.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        payment = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='create',
            object_id=payment.id,
            description=(
                f'Created payment '
                f'{payment.amount}'
            )
        )

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('finance')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class PaymentDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = PaymentSerializer

    def get_queryset(self):

        return Payment.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        payment = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='update',
            object_id=payment.id,
            description=(
                f'Updated payment '
                f'{payment.amount}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted payment '
                f'{instance.amount}'
            )
        )

        instance.delete()

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('finance')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('finance')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('finance')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ExpenseListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ExpenseSerializer

    def get_queryset(self):

        return Expense.objects.filter(
            company=self.request.user.company
        )

    def perform_create(self, serializer):

        expense = serializer.save(
            company=self.request.user.company
        )

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='create',
            object_id=expense.id,
            description=(
                f'Created expense '
                f'{expense.title}'
            )
        )

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('finance')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ExpenseDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ExpenseSerializer

    def get_queryset(self):

        return Expense.objects.filter(
            company=self.request.user.company
        )

    def perform_update(self, serializer):

        expense = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='update',
            object_id=expense.id,
            description=(
                f'Updated expense '
                f'{expense.title}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted expense '
                f'{instance.title}'
            )
        )

        instance.delete()

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('finance')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('finance')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('finance')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
#invoice 
class InvoiceListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = InvoiceSerializer

    def get_queryset(self):

        return Invoice.objects.filter(
            student__company=self.request.user.company
        )

    def perform_create(self, serializer):

        invoice = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='create',
            object_id=invoice.id,
            description=(
                f'Created invoice '
                f'{invoice.invoice_number}'
            )
        )

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('finance')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class InvoiceDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = InvoiceSerializer

    def get_queryset(self):

        return Invoice.objects.filter(
            student__company=self.request.user.company
        )

    def perform_update(self, serializer):

        invoice = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='update',
            object_id=invoice.id,
            description=(
                f'Updated invoice '
                f'{invoice.invoice_number}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted invoice '
                f'{instance.invoice_number}'
            )
        )

        instance.delete()

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('finance')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('finance')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('finance')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
class ReceiptListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = ReceiptSerializer

    def get_queryset(self):

        return Receipt.objects.filter(
            payment__company=self.request.user.company
        )

    def perform_create(self, serializer):

        receipt = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='create',
            object_id=receipt.id,
            description=(
                f'Created receipt '
                f'{receipt.receipt_number}'
            )
        )

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('finance')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class ReceiptDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = ReceiptSerializer

    def get_queryset(self):

        return Receipt.objects.filter(
            payment__company=self.request.user.company
        )

    def perform_update(self, serializer):

        receipt = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='update',
            object_id=receipt.id,
            description=(
                f'Updated receipt '
                f'{receipt.receipt_number}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted receipt '
                f'{instance.receipt_number}'
            )
        )

        instance.delete()

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('finance')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('finance')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('finance')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
    
#refunds
class RefundListCreateAPIView(
    generics.ListCreateAPIView
):

    serializer_class = RefundSerializer

    def get_queryset(self):

        return Refund.objects.filter(
            payment__company=self.request.user.company
        )

    def perform_create(self, serializer):

        refund = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='create',
            object_id=refund.id,
            description=(
                f'Created refund '
                f'{refund.amount}'
            )
        )

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)

    @module_required('finance')
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)


class RefundDetailAPIView(
    generics.RetrieveUpdateDestroyAPIView
):

    serializer_class = RefundSerializer

    def get_queryset(self):

        return Refund.objects.filter(
            payment__company=self.request.user.company
        )

    def perform_update(self, serializer):

        refund = serializer.save()

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='update',
            object_id=refund.id,
            description=(
                f'Updated refund '
                f'{refund.amount}'
            )
        )

    def perform_destroy(self, instance):

        AuditLogService.log(
            company=self.request.user.company,
            user=self.request.user,
            module='Finance',
            action='delete',
            object_id=instance.id,
            description=(
                f'Deleted refund '
                f'{instance.amount}'
            )
        )

        instance.delete()

    @module_required('finance')
    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    @module_required('finance')
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @module_required('finance')
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    @module_required('finance')
    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)