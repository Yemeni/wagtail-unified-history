from django.apps import AppConfig


class WagtailUnifiedHistoryConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'wagtail_unified_history'


    # def ready(self):
    #     from wagtail.log_actions import registry

    #     if not registry.has_scanned_for_actions:
    #         registry.scan_for_actions()