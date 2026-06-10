from django.urls import path

from .api_views import DashboardAPIView

urlpatterns = [

    path(
        '',
        DashboardAPIView.as_view(),
        name='dashboard'
    ),

]