from django.urls import path

from .api_views import (
    PartnerUniversityListCreateAPIView,
    PartnerUniversityDetailAPIView,
    PartnerContactListCreateAPIView,
    PartnerContactDetailAPIView,
    PartnerAgreementListCreateAPIView,
    PartnerAgreementDetailAPIView,
    PartnerCommissionListCreateAPIView,
    PartnerCommissionDetailAPIView,
)

urlpatterns = [

    # Universities

    path(
        'universities/',
        PartnerUniversityListCreateAPIView.as_view(),
        name='partner-university-list'
    ),

    path(
        'universities/<int:pk>/',
        PartnerUniversityDetailAPIView.as_view(),
        name='partner-university-detail'
    ),

    # Contacts

    path(
        'contacts/',
        PartnerContactListCreateAPIView.as_view(),
        name='partner-contact-list'
    ),

    path(
        'contacts/<int:pk>/',
        PartnerContactDetailAPIView.as_view(),
        name='partner-contact-detail'
    ),

    # Agreements

    path(
        'agreements/',
        PartnerAgreementListCreateAPIView.as_view(),
        name='partner-agreement-list'
    ),

    path(
        'agreements/<int:pk>/',
        PartnerAgreementDetailAPIView.as_view(),
        name='partner-agreement-detail'
    ),

    # Commissions

    path(
        'commissions/',
        PartnerCommissionListCreateAPIView.as_view(),
        name='partner-commission-list'
    ),

    path(
        'commissions/<int:pk>/',
        PartnerCommissionDetailAPIView.as_view(),
        name='partner-commission-detail'
    ),
]