import pandas as pd
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from locations.models import Village


class Command(BaseCommand):
    help = 'Part 5: Imports Villages (Bulk Mode)'

    def handle(self, *args, **kwargs):
        self.stdout.write("Reading Excel... (This takes memory)")
        try:
            df = pd.read_excel('data/All_Villages.xlsx')
            village_objs = []

            self.stdout.write("Processing rows...")
            for _, row in df.iterrows():
                try:
                    if pd.isna(row['Village Code']) or pd.isna(row['Sub-District Code']):
                        continue

                    v = Village(
                        id=int(row['Village Code']),
                        sub_district_id=int(row['Sub-District Code']),
                        name=str(row['Village Name (In English)']).strip(),
                        category=row.get('Village Category', 'Rural'),
                        slug=slugify(str(row['Village Name (In English)']))
                    )
                    village_objs.append(v)

                    # Save every 5000 records to keep RAM usage low
                    if len(village_objs) >= 5000:
                        Village.objects.bulk_create(
                            village_objs, ignore_conflicts=True)
                        village_objs = []
                        self.stdout.write(".", ending="")  # Progress dots

                except Exception:
                    continue  # Skip bad rows

            # Save any remaining villages
            if village_objs:
                Village.objects.bulk_create(
                    village_objs, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                "\n✓ Villages Imported Successfully"))

        except FileNotFoundError:
            self.stderr.write("File not found: data/All_Villages.xlsx")
        except Exception as e:
            self.stderr.write(f"Critical Error: {e}")
