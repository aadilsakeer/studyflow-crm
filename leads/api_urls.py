from django.urls import path

from .api_views import LeadListAPIView

urlpatterns = [
    path(
        '',
        LeadListAPIView.as_view(),
        name='lead-list'
    ),
]