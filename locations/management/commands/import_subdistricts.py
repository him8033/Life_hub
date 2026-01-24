import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from locations.models import SubDistrict


class Command(BaseCommand):
    help = 'Part 4: Imports Sub-Districts (Tehsils)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Importing Sub-Districts...")
        try:
            df = pd.read_excel('data/All_SubDistricts.xlsx')

            for _, row in df.iterrows():
                if pd.isna(row['Sub-district Code']) or pd.isna(row['Sub-district Name']):
                    continue

                SubDistrict.objects.update_or_create(
                    id=int(row['Sub-district Code']),
                    defaults={
                        'district_id': int(row['District Code']),
                        'name': str(row['Sub-district Name']).strip(),
                        'slug': slugify(str(row['Sub-district Name']))
                    }
                )
            self.stdout.write(self.style.SUCCESS(
                "✓ Sub-Districts Imported Successfully"))

        except FileNotFoundError:
            self.stderr.write("File not found: data/All_SubDistricts.xlsx")
        except Exception as e:
            self.stderr.write(f"Critical Error: {e}")
