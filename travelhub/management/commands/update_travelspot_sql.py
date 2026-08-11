import re

from django.core.management.base import BaseCommand

from life_hub.utils import generate_ulid_with_prefix


class Command(BaseCommand):
    help = (
        "Add/regenerate id and travelspot_id values "
        "in TravelSpot SQL"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "input_file",
            type=str,
            help="Input TravelSpot SQL file",
        )

        parser.add_argument(
            "--output",
            type=str,
            default="travel_spots_updated.sql",
            help="Output SQL file",
        )

    def handle(self, *args, **options):
        input_file = options["input_file"]
        output_file = options["output"]

        with open(
            input_file,
            "r",
            encoding="utf-8",
        ) as f:
            sql = f.read()

        counter = 1

        # ---------------------------------------------------------
        # Replace id and travelspot_id inside every VALUES row
        #
        # Before:
        #
        # (
        #     1,
        #     'trv_delhi_popular_001',
        #     'Red Fort',
        #
        # After:
        #
        # (
        #     1,
        #     'trv_01K...',
        #     'Red Fort',
        # ---------------------------------------------------------

        pattern = re.compile(
            r"""
            \(\s*
            (\d+)
            \s*,\s*
            '([^']*)'
            \s*,
            """,
            re.VERBOSE,
        )

        def replace(match):
            nonlocal counter

            travelspot_id = generate_ulid_with_prefix("trv")

            result = (
                f"(\n"
                f"        {counter},\n"
                f"        '{travelspot_id}',"
            )

            counter += 1

            return result

        sql = pattern.sub(
            replace,
            sql,
        )

        # ---------------------------------------------------------
        # Write output
        # ---------------------------------------------------------

        with open(
            output_file,
            "w",
            encoding="utf-8",
        ) as f:
            f.write(sql)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {counter - 1} TravelSpot rows."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved to {output_file}"
            )
        )
