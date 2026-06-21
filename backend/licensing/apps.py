from django.apps import AppConfig


class LicensingConfig(AppConfig):
    name = 'licensing'

    def ready(self):
        import licensing.signals  # noqa: F401
