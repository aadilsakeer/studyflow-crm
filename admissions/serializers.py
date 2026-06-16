from rest_framework import serializers

from .models import (
    Student,
    Application,
    Document,
    VisaCase,
    University,
    Course,
    OfferLetter,
    SupportTicket,
    TicketComment
)


class StudentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Student
        fields = "__all__"


class ApplicationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Application
        fields = "__all__"
class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"


class VisaCaseSerializer(serializers.ModelSerializer):

    class Meta:
        model = VisaCase
        fields = "__all__"


class UniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = University
        fields = "__all__"


class CourseSerializer(serializers.ModelSerializer):

    class Meta:
        model = Course
        fields = "__all__"


class OfferLetterSerializer(serializers.ModelSerializer):

    class Meta:
        model = OfferLetter
        fields = "__all__"


class SupportTicketSerializer(serializers.ModelSerializer):

    class Meta:
        model = SupportTicket
        fields = "__all__"


class TicketCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = TicketComment
        fields = "__all__"