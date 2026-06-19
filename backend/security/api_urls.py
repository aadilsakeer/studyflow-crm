from django.urls import path

from .api_views import (
    PasswordPolicyCheckAPIView,
    RevokeSessionsAPIView,
    SecurityDashboardAPIView,
    TwoFAEnableAPIView,
    TwoFASetupAPIView,
    UserSecurityEventsAPIView,
)

urlpatterns = [
    path('2fa/setup/', TwoFASetupAPIView.as_view()),
    path('2fa/enable/', TwoFAEnableAPIView.as_view()),
    path('dashboard/', SecurityDashboardAPIView.as_view()),
    path('events/', UserSecurityEventsAPIView.as_view()),
    path('sessions/revoke/', RevokeSessionsAPIView.as_view()),
    path('password/check/', PasswordPolicyCheckAPIView.as_view()),
]