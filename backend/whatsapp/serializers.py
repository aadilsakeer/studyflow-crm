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
        fields = (
            "id",
            "company",
            "user",
            "phone_number",
            "is_connected",
            "last_connected_at",
            "created_at",
        )
        read_only_fields = (
            "company",
            "user",
            "is_connected",
            "last_connected_at",
            "created_at",
        )


class WhatsAppMessageSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WhatsAppMessage
        fields = (
            "id",
            "company",
            "account",
            "lead",
            "student",
            "recipient_number",
            "message",
            "message_type",
            "status",
            "created_at",
        )
        read_only_fields = (
            "company",
            "status",
            "created_at",
        )


class WhatsAppServerSerializer(
    serializers.ModelSerializer
):

    class Meta:
        model = WhatsAppServer
        fields = (
            "id",
            "company",
            "base_url",
            "api_key",
            "is_active",
        )
        read_only_fields = (
            "company",
        )
        extra_kwargs = {
            "api_key": {"write_only": True},
        }
