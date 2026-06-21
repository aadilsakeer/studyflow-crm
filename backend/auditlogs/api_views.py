from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from accounts.constants import PERM_REPORTS_VIEW
from accounts.permissions import (
    IsCompanyMember,
    permission_required,
)

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListAPIView(generics.ListAPIView):
    serializer_class = AuditLogSerializer
    permission_classes = [
        IsAuthenticated,
        IsCompanyMember,
        permission_required(PERM_REPORTS_VIEW),
    ]

    def get_queryset(self):
        company = getattr(self.request.user, 'company', None)

        if not company:
            return AuditLog.objects.none()

        return AuditLog.objects.filter(
            company=company,
        ).select_related(
            'user',
        ).order_by('-created_at')
