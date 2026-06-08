from rest_framework.generics import ListAPIView

from .models import (
    Student,
    Application,
)

from .serializers import (
    StudentSerializer,
    ApplicationSerializer,
)


class StudentListAPIView(ListAPIView):

    queryset = Student.objects.all()
    serializer_class = StudentSerializer


class ApplicationListAPIView(ListAPIView):

    queryset = Application.objects.all()
    serializer_class = ApplicationSerializer