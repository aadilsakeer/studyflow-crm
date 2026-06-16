from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView,
)

from leads.models import FollowUp
from .serializers import (
    FollowUpSerializer,
)


class FollowUpListAPIView(
    ListCreateAPIView
):
    queryset = FollowUp.objects.all()
    serializer_class = (
        FollowUpSerializer
    )


class FollowUpDetailAPIView(
    RetrieveUpdateDestroyAPIView
):
    queryset = FollowUp.objects.all()
    serializer_class = (
        FollowUpSerializer
    )