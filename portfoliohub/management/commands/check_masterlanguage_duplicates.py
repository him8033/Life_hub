import re

from collections import defaultdict

from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = "Check duplicate master language names, slugs and codes"

    def add_arguments(self, parser):

        parser.add_argument(
            "sql_file",
            type=str,
        )

    def handle(self, *args, **options):

        with open(
            options["sql_file"],
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        pattern = re.compile(
            r"""
            \(
            \s*(\d+)\s*,

            \s*'([^']+)'\s*,

            \s*'([^']+)'\s*,

            \s*'([^']+)'\s*,

            \s*'([^']+)'\s*,

            \s*'([^']*)'\s*,

            \s*(\d+)\s*,

            \s*(true|false)\s*,

            \s*CURRENT_TIMESTAMP\s*,

            \s*CURRENT_TIMESTAMP

            \)
            """,
            re.VERBOSE | re.IGNORECASE | re.DOTALL
        )

        duplicate_names = defaultdict(list)
        duplicate_slugs = defaultdict(list)
        duplicate_codes = defaultdict(list)

        total = 0

        for m in pattern.finditer(content):

            total += 1

            row = {

                "id": m.group(1),

                "masterlanguage_id": m.group(2),

                "name": m.group(3),

                "slug": m.group(4),

                "code": m.group(5),

                "icon": m.group(6),

                "position": m.group(7),

                "is_active": m.group(8),

            }

            duplicate_names[row["name"].lower()].append(row)
            duplicate_slugs[row["slug"].lower()].append(row)
            duplicate_codes[row["code"].lower()].append(row)

        print("=" * 120)
        print("MASTER LANGUAGE DUPLICATE REPORT")
        print("=" * 120)
        print(f"Total Languages : {total}")

        def print_duplicates(title, data, field):

            duplicates = {
                k: v
                for k, v in data.items()
                if len(v) > 1
            }

            print("\n")
            print("=" * 120)
            print(title)
            print("=" * 120)

            print(f"Duplicate Count : {len(duplicates)}")

            total_rows = 0

            for key, rows in sorted(duplicates.items()):

                print(f"\n{key.upper()} ({len(rows)} rows)")
                print("-" * 120)

                for r in rows:

                    total_rows += 1

                    print(
                        f"ID : {r['id']} | "
                        f"MasterLanguage ID : {r['masterlanguage_id']} | "
                        f"Name : {r['name']:<30} | "
                        f"{field} : {r[field]}"
                    )

            print("\n")
            print(f"Total Duplicate Rows : {total_rows}")

        print_duplicates(
            "DUPLICATE LANGUAGE NAMES",
            duplicate_names,
            "slug",
        )

        print_duplicates(
            "DUPLICATE LANGUAGE SLUGS",
            duplicate_slugs,
            "code",
        )

        print_duplicates(
            "DUPLICATE LANGUAGE CODES",
            duplicate_codes,
            "code",
        )
