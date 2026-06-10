from rest_framework import serializers

from .models import (
    Agent,
    AgentCommission
)


class AgentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Agent
        fields = '__all__'


class AgentCommissionSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = AgentCommission
        fields = '__all__'