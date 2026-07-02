from django.apps import AppConfig


class ContentConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "content"
    verbose_name = "CMS"

    def ready(self):
        # === FEATURE: cms ===
        # Register cache-invalidation signals for server-rendered CMS pages.
        import content.signals  # noqa: F401
        # === END FEATURE: cms ===
