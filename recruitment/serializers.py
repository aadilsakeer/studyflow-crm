from rest_framework import serializers

from .models import (
    Employer,
    JobOpening,
    Candidate,
    Interview,
    Deployment
)


class EmployerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Employer
        fields = '__all__'


class JobOpeningSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobOpening
        fields = '__all__'


class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = '__all__'


class InterviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interview
        fields = '__all__'


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = '__all__'