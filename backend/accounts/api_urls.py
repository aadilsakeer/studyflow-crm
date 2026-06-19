from django.urls import path

from .api_views import CurrentUserAPIView, StaffUserManagementAPIView


urlpatterns = [
    path(
        "me/",
        CurrentUserAPIView.as_view(),
        name="current-user",
    ),
    path(
        "staff/<int:user_id>/",
        StaffUserManagementAPIView.as_view(),
    ),
]
