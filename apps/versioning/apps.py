"""
Versioning app configuration
"""
from django.apps import AppConfig


class VersioningConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.versioning'
    verbose_name = 'App Versioning'