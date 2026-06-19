from django.urls import path

from .api_health import HealthCheckAPIView, LaunchChecklistAPIView, OperationsDashboardAPIView

urlpatterns = [
    path('', HealthCheckAPIView.as_view()),
    path('operations/', OperationsDashboardAPIView.as_view()),
    path('launch-checklist/', LaunchChecklistAPIView.as_view()),
]
