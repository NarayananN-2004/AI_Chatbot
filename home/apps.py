from django.apps import AppConfig


# class HomeConfig(AppConfig):
#     name = 'home'

class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        from home.ml_utils import JarvisEngine
        self.engine = JarvisEngine()