from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    # def ready(self):
    #     from .qdrant_service import init_collection
    #     init_collection()
