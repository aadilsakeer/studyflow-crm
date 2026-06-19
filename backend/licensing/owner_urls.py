from django.urls import path

from .owner_views import (
    OwnerCompanyDetailAPIView,
    OwnerCompanyListCreateAPIView,
    OwnerDashboardAPIView,
    OwnerImpersonateAPIView,
)

urlpatterns = [
    path('dashboard/', OwnerDashboardAPIView.as_view()),
    path('companies/', OwnerCompanyListCreateAPIView.as_view()),
    path('companies/<int:company_id>/', OwnerCompanyDetailAPIView.as_view()),
    path('companies/<int:company_id>/impersonate/', OwnerImpersonateAPIView.as_view()),
]
