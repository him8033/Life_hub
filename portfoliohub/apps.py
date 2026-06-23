from django.apps import AppConfig


class PortfoliohubConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'portfoliohub'


class PortfoliohubConfig(AppConfig):

    default_auto_field = "django.db.models.BigAutoField"

    name = "portfoliohub"

    def ready(self):

        import portfoliohub.signals
