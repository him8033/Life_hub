import re

from django.core.management.base import BaseCommand

from life_hub.utils import generate_ulid_with_prefix


class Command(BaseCommand):

    help = "Add id, masterskill_id, created_at and updated_at to MasterSkill SQL"

    def add_arguments(self, parser):

        parser.add_argument(
            "input_file",
            type=str
        )

        parser.add_argument(
            "--output",
            type=str,
            default="master_skills_updated.sql",
        )

    def handle(self, *args, **options):

        input_file = options["input_file"]
        output_file = options["output"]

        with open(
            input_file,
            "r",
            encoding="utf-8"
        ) as f:

            sql = f.read()

        # Update INSERT columns
        sql = re.sub(
            r'\("category_id",\s*"name",\s*"slug",\s*"icon",\s*"description",\s*"is_active",\s*"priority"\)',
            '("id", "masterskill_id", "category_id", "name", "slug", "icon", "description", "is_active", "priority", "created_at", "updated_at")',
            sql,
        )

        counter = 1

        # Replace VALUES beginning
        pattern = re.compile(
            r"\(\s*(\d+),\s*'"
        )

        def replace(match):

            nonlocal counter

            category_id = match.group(1)

            result = (
                f"({counter},"
                f"'{generate_ulid_with_prefix('msk')}',"
                f"{category_id},'"
            )

            counter += 1

            return result

        sql = pattern.sub(
            replace,
            sql
        )

        # Add timestamps after priority
        #
        # Before:
        # true, 1),
        #
        # After:
        # true, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP),
        #

        sql = re.sub(
            r",\s*(\d+)\s*\)",
            r",\1,CURRENT_TIMESTAMP,CURRENT_TIMESTAMP)",
            sql,
        )

        with open(
            output_file,
            "w",
            encoding="utf-8"
        ) as f:

            f.write(sql)

        self.stdout.write(
            self.style.SUCCESS(
                f"Generated {counter - 1} rows."
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Saved to {output_file}"
            )
        )
