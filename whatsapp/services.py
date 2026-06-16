import uuid

from .models import (
    WhatsAppAccount,
    WhatsAppMessage
)


class WhatsAppService:

    @staticmethod
    def create_session():

        return str(
            uuid.uuid4()
        )

    @staticmethod
    def log_message(
        company,
        account,
        recipient_number,
        message,
        status='pending',
        response_data=''
    ):

        return WhatsAppMessage.objects.create(
            company=company,
            account=account,
            recipient_number=recipient_number,
            message=message,
            status=status,
            response_data=response_data
        )

    @staticmethod
    def get_account_for_user(user):

        try:

            return WhatsAppAccount.objects.get(
                user=user,
                is_connected=True
            )

        except WhatsAppAccount.DoesNotExist:

            return None