from rest_framework import serializers

from .models import (
    WhatsAppAccount,
    WhatsAppMessage,
    WhatsAppServer
)


class WhatsAppAccountSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WhatsAppAccount
        fields = '__all__'


class WhatsAppMessageSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WhatsAppMessage
        fields = '__all__'


class WhatsAppServerSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WhatsAppServer
        fields = '__all__'