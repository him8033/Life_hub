import pandas as pd
from django.core.management.base import BaseCommand
from locations.models import Pincode


class Command(BaseCommand):
    help = 'Part 6: Imports Pincode Mappings'

    def handle(self, *args, **kwargs):
        self.stdout.write("Reading Pincode Data...")
        try:
            df = pd.read_excel('data/Pincode_Mapping.xlsx')
            pin_objs = []

            for _, row in df.iterrows():
                try:
                    if pd.isna(row['Pincode']) or pd.isna(row['Village Code']):
                        continue

                    # Note: We treat Pincode as string to preserve leading zeros if any
                    p = Pincode(
                        pincode=str(int(row['Pincode'])),
                        village_id=int(row['Village Code'])
                    )
                    pin_objs.append(p)

                    if len(pin_objs) >= 5000:
                        Pincode.objects.bulk_create(
                            pin_objs, ignore_conflicts=True)
                        pin_objs = []
                        self.stdout.write(".", ending="")
                except Exception:
                    continue

            if pin_objs:
                Pincode.objects.bulk_create(pin_objs, ignore_conflicts=True)

            self.stdout.write(self.style.SUCCESS(
                "\n✓ Pincodes Imported Successfully"))

        except FileNotFoundError:
            self.stderr.write("File not found: data/Pincode_Mapping.xlsx")
        except Exception as e:
            self.stderr.write(f"Critical Error: {e}")
