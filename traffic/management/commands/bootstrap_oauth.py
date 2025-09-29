from django.core.management.base import BaseCommand
from oauth2_provider.models import Application
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        User = get_user_model()
        user = User.objects.first()
        if not user:
            self.stdout.write("no user; create one first")
            return
        app, _ = Application.objects.get_or_create(
            name="TransitApp",
            client_type=Application.CLIENT_CONFIDENTIAL,
            authorization_grant_type=Application.GRANT_AUTHORIZATION_CODE,
            user=user,
            redirect_uris="http://localhost:8000/authorized",
        )
        self.stdout.write(f"client_id={app.client_id}")
        self.stdout.write(f"client_secret={app.client_secret}")
