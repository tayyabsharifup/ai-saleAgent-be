from django.apps import AppConfig


class AimoduleConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.aiModule'

    def ready(self):
        import apps.aiModule.signals

