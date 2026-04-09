from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os


class Command(BaseCommand):
    help = "Create superuser from environment variables"

    def handle(self, *args, **kwargs):
        User = get_user_model()

        email = os.getenv("DJANGO_SUPERUSER_EMAIL")
        password = os.getenv("DJANGO_SUPERUSER_PASSWORD")
        name = os.getenv("DJANGO_SUPERUSER_NAME")
        tc = os.getenv("DJANGO_SUPERUSER_TC") == "True"

        if not email or not password:
            self.stdout.write(self.style.ERROR("Missing env variables"))
            return

        if User.objects.filter(email=email).exists():
            self.stdout.write("Superuser already exists")
            return

        User.objects.create_superuser(
            email=email,
            password=password,
            name=name,
            tc=tc,
        )

        self.stdout.write(self.style.SUCCESS("Superuser created successfully"))
