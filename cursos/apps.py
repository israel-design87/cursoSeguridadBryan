from django.apps import AppConfig


class CursosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'cursos'


    def ready(self):
        import cursos.signals  # 👈 esto es esencial
