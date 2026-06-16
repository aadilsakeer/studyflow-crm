from rest_framework import serializers

from .models import ClientPortalAccess


class ClientPortalAccessSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = ClientPortalAccess
        fields = '__all__'