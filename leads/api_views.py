from rest_framework.generics import ListCreateAPIView

from .models import Lead
from .serializers import LeadSerializer


class LeadListAPIView(ListCreateAPIView):

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer