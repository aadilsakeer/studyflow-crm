from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenBlacklistView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path(
        'api/token/',
        TokenObtainPairView.as_view(),
        name='token_obtain_pair'
    ),

    path(
        'api/token/refresh/',
        TokenRefreshView.as_view(),
        name='token_refresh'
    ),

    path(
        'api/token/blacklist/',
        TokenBlacklistView.as_view(),
        name='token_blacklist'
    ),

    path(
        'api/',
        include('accounts.api_urls')
    ),

    path(
        'api/leads/',
        include('leads.api_urls')
    ),

    path(
        'api/',
        include('admissions.api_urls')
    ),

    path(
        'api/reports/',
        include('reports.api_urls')
    ),

    path(
        'api/activity/',
        include('activity.api_urls'),
    ),

    path(
        'api/dashboard/',
        include('dashboard.api_urls')
    ),

    path(
        'api/partners/',
        include('partners.api_urls')
    ),

    path(
        'api/agents/',
        include('agents.api_urls')
    ),

    path(
        'api-auth/',
        include('rest_framework.urls')
    ),

    path(
        'api/recruitment/',
        include('recruitment.api_urls')
    ),

    path(
        'api/workvisa/',
        include('workvisa.api_urls')
    ),

    path(
        'api/auditlogs/',
        include('auditlogs.api_urls')
    ),

    path(
        'api/finance/',
        include('finance.api_urls')
    ),

    path(
        'api/hrm/',
        include('hrm.api_urls')
    ),

    path(
        'api/portal/',
        include('clientportal.portal_urls'),
    ),

    path(
        'api/clientportal/',
        include('clientportal.api_urls')
    ),

    path(
        'api/whatsapp/',
        include('whatsapp.api_urls')
    ),

    path(
        'api/tasks/',
        include('core.task_urls'),
    ),

    path(
        'api/followups/',
        include('followups.api_urls')
    ),

    path(
        'api/calllogs/',
        include('calllogs.api_urls')
    ),

    path(
        'api/notifications/',
        include('notifications.api_urls')
    ),
]

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT,
    )
