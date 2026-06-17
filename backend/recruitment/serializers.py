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
        fields = (
            "id",
            "company",
            "name",
            "contact_person",
            "phone",
            "email",
            "country",
            "is_active",
        )
        read_only_fields = (
            "company",
        )


class JobOpeningSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobOpening
        fields = (
            "id",
            "employer",
            "title",
            "country",
            "vacancies",
            "salary",
            "requirements",
            "status",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )


class CandidateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Candidate
        fields = (
            "id",
            "company",
            "assigned_staff",
            "full_name",
            "phone",
            "email",
            "passport_number",
            "preferred_country",
            "status",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class InterviewSerializer(serializers.ModelSerializer):

    class Meta:
        model = Interview
        fields = (
            "id",
            "candidate",
            "interview_date",
            "interviewer",
            "remarks",
            "status",
        )


class DeploymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Deployment
        fields = (
            "id",
            "candidate",
            "employer",
            "joining_date",
            "country",
            "remarks",
        )
