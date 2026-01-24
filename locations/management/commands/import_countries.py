from django.core.management.base import BaseCommand
from django.utils.text import slugify
from locations.models import Country


class Command(BaseCommand):
    help = 'Part 1: Creates the root Country (India)'

    def handle(self, *args, **kwargs):
        try:
            # We explicitly set ID=1 so all States can link to it easily
            obj, created = Country.objects.get_or_create(
                id=1,
                defaults={
                    'name': "India",
                    'iso_code': "IN",
                    'slug': "india"
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(
                    "✓ Created Country: India"))
            else:
                self.stdout.write(self.style.WARNING("ℹ India already exists"))
        except Exception as e:
            self.stderr.write(f"Error creating country: {e}")
