from django.apps import AppConfig
import os

class TrafficConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "traffic"

    def ready(self):
        if os.environ.get("ENABLE_SCHEDULER", "1") == "1":
            try:
                from .scheduler import start_scheduler
                start_scheduler()
            except Exception:
                pass
