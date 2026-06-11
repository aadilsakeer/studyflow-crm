from rest_framework import generics

from .models import AuditLog
from .serializers import AuditLogSerializer


class AuditLogListAPIView(
    generics.ListAPIView
):

    serializer_class = AuditLogSerializer

    def get_queryset(self):

        return AuditLog.objects.filter(
            company=self.request.user.company
        ).order_by(
            '-created_at'
        )