from rest_framework import serializers
from leads.models import FollowUp


class FollowUpSerializer(
    serializers.ModelSerializer
):
    class Meta:
        model = FollowUp
        fields = "__all__"