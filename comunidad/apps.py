from django.apps import AppConfig


class ComunidadConfig(AppConfig):
    name = 'comunidad'

    def ready(self):
        import comunidad.signals  # noqa: F401
