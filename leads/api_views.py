from rest_framework.generics import ListAPIView

from .models import Lead
from .serializers import LeadSerializer


class LeadListAPIView(ListAPIView):

    queryset = Lead.objects.all()
    serializer_class = LeadSerializer