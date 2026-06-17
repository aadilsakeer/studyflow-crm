from django.contrib.auth.hashers import (
    make_password,
    check_password
)


class ClientPortalAuthService:

    @staticmethod
    def hash_password(password):

        return make_password(password)

    @staticmethod
    def verify_password(
        raw_password,
        hashed_password
    ):

        return check_password(
            raw_password,
            hashed_password
        )