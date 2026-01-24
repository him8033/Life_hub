import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from locations.models import State


class Command(BaseCommand):
    help = 'Part 2: Imports States'

    def handle(self, *args, **kwargs):
        self.stdout.write("Importing States...")
        try:
            df = pd.read_excel('data/All_States.xlsx')

            for _, row in df.iterrows():
                if pd.isna(row['State Code']) or pd.isna(row['State Name (In English)']):
                    continue

                State.objects.update_or_create(
                    id=int(row['State Code']),
                    defaults={
                        'country_id': 1,  # Links to India
                        'name': str(row['State Name (In English)']).strip(),
                        'type': row.get('State or UT', 'State'),
                        'slug': slugify(str(row['State Name (In English)']))
                    }
                )
            self.stdout.write(self.style.SUCCESS(
                "✓ States Imported Successfully"))

        except FileNotFoundError:
            self.stderr.write("File not found: data/All_States.xlsx")
        except Exception as e:
            self.stderr.write(f"Critical Error: {e}")
