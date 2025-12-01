"""Django app configuration for DJGramm."""

from django.apps import AppConfig


class DjgrammAppConfig(AppConfig):
    """Configuration for the main DJGramm application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "app"
    verbose_name = "DJGramm"

    def ready(self):
        """Import signals when app is ready."""
        from . import signals  # noqa: F401
