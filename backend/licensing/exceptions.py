from rest_framework.exceptions import APIException


class LimitExceededError(APIException):
    status_code = 402
    default_detail = 'Plan usage limit reached.'
    default_code = 'limit_exceeded'


class SubscriptionInactiveError(APIException):
    status_code = 403
    default_detail = 'Subscription is not active.'
    default_code = 'subscription_inactive'
