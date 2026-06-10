from rest_framework import serializers

from .models import (
    PartnerUniversity,
    PartnerContact,
    PartnerAgreement,
    PartnerCommission
)


class PartnerUniversitySerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerUniversity
        fields = '__all__'


class PartnerContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerContact
        fields = '__all__'


class PartnerAgreementSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerAgreement
        fields = '__all__'


class PartnerCommissionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PartnerCommission
        fields = '__all__'