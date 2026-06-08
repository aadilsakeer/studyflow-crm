from rest_framework import serializers

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    OfferLetter,
)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = "__all__"