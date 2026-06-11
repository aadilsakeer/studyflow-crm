from django.contrib import admin
from django.urls import path, include

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    # JWT Authentication
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

    # Leads APIs
    path(
        'api/leads/',
        include('leads.api_urls')
    ),

    # Admissions APIs
    path(
        'api/',
        include('admissions.api_urls')
    ),
    path(
         'api/reports/',
        include('reports.api_urls')
    ),
    path(
         'api/dashboard/',
         include('core.api_urls')
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
]