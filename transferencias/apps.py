from django.apps import AppConfig


class TransferenciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transferencias'
# transferencias/apps.py
from django.apps import AppConfig

class TransferenciasConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'transferencias'

    def ready(self):
        import transferencias.signals
