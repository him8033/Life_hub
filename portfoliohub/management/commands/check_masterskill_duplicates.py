from django.core.management.base import BaseCommand

import re
from collections import defaultdict


class Command(BaseCommand):

    help = "Check duplicate master skill names and slugs"

    def add_arguments(self, parser):

        parser.add_argument(
            "sql_file",
            type=str,
            help="Path to master skill SQL file"
        )

    def handle(self, *args, **options):

        sql_file = options["sql_file"]

        """
        SQL Format:

        (
            id,
            masterskill_id,
            category_id,
            name,
            slug,
            icon,
            description,
            is_active,
            priority,
            created_at,
            updated_at
        )

        """

        pattern = re.compile(
            r"""
            \(
                \s*(\d+)\s*,                       # id

                \s*'([^']+)'\s*,                   # masterskill_id

                \s*(\d+)\s*,                       # category_id

                \s*'([^']+)'\s*,                   # name

                \s*'([^']+)'\s*,                   # slug

                \s*'([^']*)'\s*,                   # icon

                \s*'(.*?)'\s*,                     # description

                \s*(true|false)\s*,                # is_active

                \s*(\d+)\s*,                       # priority

                \s*CURRENT_TIMESTAMP\s*,

                \s*CURRENT_TIMESTAMP

            \)
            """,
            re.IGNORECASE | re.VERBOSE | re.DOTALL
        )

        duplicate_names = defaultdict(list)

        duplicate_slugs = defaultdict(list)

        with open(
            sql_file,
            "r",
            encoding="utf-8"
        ) as f:

            content = f.read()

        total_skills = 0

        for match in pattern.finditer(content):

            total_skills += 1

            data = {


                "id": match.group(1),


                "masterskill_id": match.group(2),


                "category_id": match.group(3),


                "name": match.group(4).strip(),


                "slug": match.group(5).strip(),


                "icon": match.group(6).strip(),


                "description": match.group(7).strip(),


                "is_active": match.group(8),


                "priority": match.group(9),


            }

            duplicate_names[
                data["name"].lower()
            ].append(data)

            duplicate_slugs[
                data["slug"].lower()
            ].append(data)

        # ============================================
        # SUMMARY
        # ============================================

        print("\n" + "=" * 120)

        print("MASTER SKILL DUPLICATE REPORT")

        print("=" * 120)

        print(
            f"Total Skills Loaded : {total_skills}"
        )

        # ============================================
        # DUPLICATE NAMES
        # ============================================

        names = {

            key: value

            for key, value in duplicate_names.items()

            if len(value) > 1

        }

        print("\n")

        print("=" * 120)

        print("DUPLICATE MASTER SKILL NAMES")

        print("=" * 120)

        print(
            f"Duplicate Names : {len(names)}"
        )

        total_rows = 0

        for name, rows in sorted(names.items()):

            print(
                f"\n{name.upper()} ({len(rows)} rows)"
            )

            print("-" * 120)

            for row in rows:

                total_rows += 1

                print(

                    f"ID : {row['id']} | "

                    f"MasterSkill ID : {row['masterskill_id']} | "

                    f"Category : {row['category_id']} | "

                    f"Slug : {row['slug']:<35}"

                )

        print("\n")

        print(
            f"Total Duplicate Name Rows : {total_rows}"
        )

        # ============================================
        # DUPLICATE SLUGS
        # ============================================

        slugs = {


            key: value


            for key, value in duplicate_slugs.items()


            if len(value) > 1

        }

        print("\n\n")

        print("=" * 120)

        print("DUPLICATE MASTER SKILL SLUGS")

        print("=" * 120)

        print(
            f"Duplicate Slugs : {len(slugs)}"
        )

        total_rows = 0

        for slug, rows in sorted(slugs.items()):

            print(
                f"\n{slug} ({len(rows)} rows)"
            )

            print("-" * 120)

            for row in rows:

                total_rows += 1

                print(

                    f"ID : {row['id']} | "

                    f"MasterSkill ID : {row['masterskill_id']} | "

                    f"Name : {row['name']:<35} | "

                    f"Category : {row['category_id']}"

                )

        print("\n")

        print(
            f"Total Duplicate Slug Rows : {total_rows}"
        )

        print("=" * 120)
