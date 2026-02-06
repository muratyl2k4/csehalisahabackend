from django.apps import AppConfig
import os

class LeaguesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leagues'
    # Explicit path to avoid ambiguity in some deployment environments (PythonAnywhere)
    path = os.path.dirname(os.path.abspath(__file__))
