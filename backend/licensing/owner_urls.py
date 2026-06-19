from django.urls import path

from .customer_success_views import (
    OwnerCustomerSuccessAlertsAPIView,
    OwnerCustomerSuccessCompanyAPIView,
    OwnerCustomerSuccessDashboardAPIView,
)
from .module_views import (
    OwnerBulkModuleAssignAPIView,
    OwnerCompanyModulesAPIView,
    OwnerModuleCatalogAPIView,
)
from .owner_views import (
    OwnerCompanyDetailAPIView,
    OwnerCompanyListCreateAPIView,
    OwnerDashboardAPIView,
    OwnerImpersonateAPIView,
    OwnerOnboardAPIView,
    OwnerUserManagementAPIView,
)

urlpatterns = [
    path('customer-success/dashboard/', OwnerCustomerSuccessDashboardAPIView.as_view()),
    path('customer-success/alerts/', OwnerCustomerSuccessAlertsAPIView.as_view()),
    path('customer-success/companies/<int:company_id>/', OwnerCustomerSuccessCompanyAPIView.as_view()),
    path('dashboard/', OwnerDashboardAPIView.as_view()),
    path('onboard/', OwnerOnboardAPIView.as_view()),
    path('modules/', OwnerModuleCatalogAPIView.as_view()),
    path('modules/bulk-assign/', OwnerBulkModuleAssignAPIView.as_view()),
    path('users/<int:user_id>/', OwnerUserManagementAPIView.as_view()),
    path('companies/', OwnerCompanyListCreateAPIView.as_view()),
    path('companies/<int:company_id>/', OwnerCompanyDetailAPIView.as_view()),
    path('companies/<int:company_id>/modules/', OwnerCompanyModulesAPIView.as_view()),
    path('companies/<int:company_id>/impersonate/', OwnerImpersonateAPIView.as_view()),
]
