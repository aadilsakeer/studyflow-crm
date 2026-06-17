from rest_framework import serializers

from .models import (
    Agent,
    AgentCommission
)


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = (
            "id",
            "company",
            "name",
            "phone",
            "email",
            "city",
            "is_active",
            "created_at",
        )
        read_only_fields = (
            "company",
            "created_at",
        )


class AgentCommissionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AgentCommission
        fields = (
            "id",
            "agent",
            "student_name",
            "amount",
            "is_paid",
            "created_at",
        )
        read_only_fields = (
            "created_at",
        )
