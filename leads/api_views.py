from rest_framework.generics import (
    ListCreateAPIView,
    RetrieveUpdateDestroyAPIView
)

from .models import Lead
from .serializers import LeadSerializer


class LeadListAPIView(ListCreateAPIView):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer


class LeadDetailAPIView(
    RetrieveUpdateDestroyAPIView
):
    queryset = Lead.objects.all()
    serializer_class = LeadSerializer