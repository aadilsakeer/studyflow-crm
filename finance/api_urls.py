from django.urls import path

from .api_views import (
    PaymentListCreateAPIView,
    PaymentDetailAPIView,
    ExpenseListCreateAPIView,
    ExpenseDetailAPIView,
    InvoiceListCreateAPIView,
    InvoiceDetailAPIView,
    ReceiptListCreateAPIView,
    ReceiptDetailAPIView,
    RefundListCreateAPIView,
    RefundDetailAPIView,
)

urlpatterns = [

    path(
        'payments/',
        PaymentListCreateAPIView.as_view()
    ),

    path(
        'payments/<int:pk>/',
        PaymentDetailAPIView.as_view()
    ),
    path(
    'expenses/',
    ExpenseListCreateAPIView.as_view()
),

path(
    'expenses/<int:pk>/',
    ExpenseDetailAPIView.as_view()
),
path(
    'invoices/',
    InvoiceListCreateAPIView.as_view()
),

path(
    'invoices/<int:pk>/',
    InvoiceDetailAPIView.as_view()
),
path(
    'receipts/',
    ReceiptListCreateAPIView.as_view()
),

path(
    'receipts/<int:pk>/',
    ReceiptDetailAPIView.as_view()
),

path(
    'refunds/',
    RefundListCreateAPIView.as_view()
),

path(
    'refunds/<int:pk>/',
    RefundDetailAPIView.as_view()
),
]