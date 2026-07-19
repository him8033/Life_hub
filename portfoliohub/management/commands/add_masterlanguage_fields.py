import re

from django.core.management.base import BaseCommand

from life_hub.utils import generate_ulid_with_prefix


class Command(BaseCommand):

    help = (
        "Add id, masterlanguage_id and created_at "
        "to MasterLanguage SQL"
    )

    def add_arguments(self, parser):

        parser.add_argument(
            "input_file",
            type=str
        )

        parser.add_argument(
            "--output",
            type=str,
            default="master_languages_updated.sql",
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

        # ---------------------------------------------------------
        # Update INSERT columns
        # Supports both:
        #
        # (name, slug, code, icon, position, is_active)
        #
        # and
        #
        # ("name","slug","code","icon","position","is_active")
        # ---------------------------------------------------------

        sql = re.sub(
            r"""
            \(
                \s*"?name"?\s*,
                \s*"?slug"?\s*,
                \s*"?code"?\s*,
                \s*"?icon"?\s*,
                \s*"?position"?\s*,
                \s*"?is_active"?\s*
            \)
            """,
            (
                '("id", "masterlanguage_id", "name", "slug", '
                '"code", "icon", "position", '
                '"is_active", "created_at")'
            ),
            sql,
            flags=re.IGNORECASE | re.VERBOSE,
        )

        counter = 1

        # ---------------------------------------------------------
        # Before:
        #
        # ('English',...
        #
        # After:
        #
        # (1,'lng_xxxxx','English',...
        # ---------------------------------------------------------

        pattern = re.compile(
            r"\(\s*'"
        )

        def replace(match):

            nonlocal counter

            value = (
                f"({counter},"
                f"'{generate_ulid_with_prefix('lng')}',"
                f"'"
            )

            counter += 1

            return value

        sql = pattern.sub(
            replace,
            sql
        )

        # ---------------------------------------------------------
        # Add created_at
        #
        # Before:
        #
        # true),
        #
        # After:
        #
        # true,CURRENT_TIMESTAMP),
        # ---------------------------------------------------------

        sql = re.sub(
            r"(,\s*(true|false))\s*\)",
            r"\1,CURRENT_TIMESTAMP)",
            sql,
            flags=re.IGNORECASE,
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
