from django.apps import AppConfig


class AppPrincipalConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'App_Principal'

    def ready(self):
        import App_Principal.signals
