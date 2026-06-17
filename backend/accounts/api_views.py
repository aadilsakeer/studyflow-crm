from rest_framework.views import APIView
from rest_framework.response import Response

from .serializers import CurrentUserSerializer


class CurrentUserAPIView(APIView):

    def get(self, request):
        serializer = CurrentUserSerializer(
            request.user,
        )

        return Response(serializer.data)
