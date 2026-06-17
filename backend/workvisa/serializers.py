from rest_framework import serializers

from .models import (
    WorkVisaCase,
    WorkVisaDocument,
    WorkVisaTimeline
)


class WorkVisaCaseSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaCase
        fields = '__all__'


class WorkVisaDocumentSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaDocument
        fields = '__all__'


class WorkVisaTimelineSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WorkVisaTimeline
        fields = '__all__'