from django.core.management.base import BaseCommand
from account.models import User
from account.models.user_profile import UserProfile


class Command(BaseCommand):
    help = "Create missing profiles for existing users"

    def handle(self, *args, **kwargs):
        users = User.objects.all()

        created_count = 0

        for user in users:
            if not hasattr(user, "profile"):
                UserProfile.objects.create(user=user)
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"{created_count} profiles created successfully")
        )
