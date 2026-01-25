from django.apps import AppConfig


class JobboardConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'jobboard'
    def ready(self):
        from . import signals  # noqa
