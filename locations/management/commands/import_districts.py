import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from locations.models import District


class Command(BaseCommand):
    help = 'Part 3: Imports Districts'

    def handle(self, *args, **kwargs):
        self.stdout.write("Importing Districts...")
        try:
            df = pd.read_excel('data/All_Districts.xlsx')

            for _, row in df.iterrows():
                if pd.isna(row['District Code']) or pd.isna(row['District Name(In English)']):
                    continue

                # Note: 'state_id' here refers to the column in the DB,
                # allowing us to pass the Integer ID directly.
                District.objects.update_or_create(
                    id=int(row['District Code']),
                    defaults={
                        'state_id': int(row['State Code']),
                        'name': str(row['District Name(In English)']).strip(),
                        'slug': slugify(str(row['District Name(In English)']))
                    }
                )
            self.stdout.write(self.style.SUCCESS(
                "✓ Districts Imported Successfully"))

        except FileNotFoundError:
            self.stderr.write("File not found: data/All_Districts.xlsx")
        except Exception as e:
            self.stderr.write(f"Critical Error: {e}")
