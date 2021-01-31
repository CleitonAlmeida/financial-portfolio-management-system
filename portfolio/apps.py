from django.apps import AppConfig


class PortfolioConfig(AppConfig):
    name = 'portfolio'

    def ready(self):
        import portfolio.signals
