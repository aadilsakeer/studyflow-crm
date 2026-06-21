import logging
import os

import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry():
    dsn = os.getenv('SENTRY_DSN', '').strip()

    if not dsn:
        return

    sentry_sdk.init(
        dsn=dsn,
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=logging.INFO,
                event_level=logging.ERROR,
            ),
        ],
        traces_sample_rate=float(
            os.getenv('SENTRY_TRACES_SAMPLE_RATE', '0.1'),
        ),
        send_default_pii=False,
        environment=os.getenv(
            'SENTRY_ENVIRONMENT',
            'production',
        ),
    )
