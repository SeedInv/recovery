# userprofile/apps.py
from django.apps import AppConfig

class UserProfileConfig(AppConfig):
    name = 'userprofile'

    def ready(self):
        import userprofile.signals