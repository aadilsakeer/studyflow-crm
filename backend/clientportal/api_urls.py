from django.urls import path

from .api_views import (
    ClientPortalAccessListCreateAPIView,
    ClientPortalAccessDetailAPIView,
)

urlpatterns = [

    path(
        '',
        ClientPortalAccessListCreateAPIView.as_view(),
        name='clientportal-list'
    ),

    path(
        '<int:pk>/',
        ClientPortalAccessDetailAPIView.as_view(),
        name='clientportal-detail'
    ),

]