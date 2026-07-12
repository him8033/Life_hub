from django.core.management.base import BaseCommand
import re
from collections import defaultdict


CATEGORY_MAP = {
    "1": "Frontend Development",
    "2": "Backend Development",
    "3": "Mobile Development",
    "4": "Data Science & AI",
    "5": "DevOps & Cloud",
    "6": "UI/UX Design",
    "7": "Cybersecurity",
    "8": "Database Management",
    "9": "Project Management",
    "10": "Digital Marketing",
    "11": "Quality Assurance",
    "12": "Business Intelligence",
    "13": "Game Development",
}


class Command(BaseCommand):
    help = "Check duplicate skill names in SQL file"

    def add_arguments(self, parser):
        parser.add_argument(
            "sql_file",
            type=str,
            help="Path to the SQL file containing INSERT statements",
        )

    def handle(self, *args, **options):
        sql_file = options["sql_file"]

        pattern = re.compile(
            r"\((.*?),'(.*?)','(.*?)','(.*?)','(.*?)',(true|false),(\d+)\)",
            re.IGNORECASE,
        )

        duplicate_names = defaultdict(list)

        with open(sql_file, "r", encoding="utf-8") as f:
            content = f.read()

        total_skills = 0

        for match in pattern.finditer(content):
            total_skills += 1

            category_id = match.group(1).strip()
            name = match.group(2).strip()
            slug = match.group(3).strip()
            icon = match.group(4).strip()
            priority = match.group(7).strip()

            duplicate_names[name.lower()].append(
                {
                    "category_id": category_id,
                    "category_name": CATEGORY_MAP.get(category_id, "Unknown"),
                    "name": name,
                    "slug": slug,
                    "icon": icon,
                    "priority": priority,
                }
            )

        duplicates = {
            k: v
            for k, v in duplicate_names.items()
            if len(v) > 1
        }

        print("\n" + "=" * 120)
        print(f"Total Skills           : {total_skills}")
        print(f"Unique Skill Names     : {len(duplicate_names)}")
        print(f"Duplicate Skill Names  : {len(duplicates)}")
        print("=" * 120)

        total_duplicate_rows = 0

        for name, rows in sorted(duplicates.items()):
            print(f"\n{name.upper()} ({len(rows)} rows)")
            print("-" * 120)

            for r in rows:
                total_duplicate_rows += 1

                print(
                    f"Category : {r['category_name']:<25} "
                    f"(ID: {r['category_id']}) | "
                    f"Slug : {r['slug']:<35} | "
                    f"Priority : {r['priority']:<4} | "
                    f"Icon : {r['icon']}"
                )

        print("\n" + "=" * 120)
        print(f"Total Duplicate Rows : {total_duplicate_rows}")
        print("=" * 120)
