import re
from collections import defaultdict

SQL_FILE = "portfoliohub_masterskill.sql"

pattern = re.compile(
    r"\((\d+),'(.*?)','(.*?)','(.*?)','(.*?)',(true|false),(\d+)\)",
    re.IGNORECASE
)

duplicate_slugs = defaultdict(list)

with open(SQL_FILE, "r", encoding="utf-8") as f:
    content = f.read()

for match in pattern.finditer(content):
    category_id = match.group(1)
    name = match.group(2)
    slug = match.group(3)
    icon = match.group(4)
    description = match.group(5)
    is_active = match.group(6)
    priority = match.group(7)

    duplicate_slugs[slug.lower()].append({
        "category_id": category_id,
        "name": name,
        "slug": slug,
        "icon": icon,
        "priority": priority
    })

duplicates = {k: v for k, v in duplicate_slugs.items() if len(v) > 1}

print("=" * 80)
print(f"Duplicate Slugs : {len(duplicates)}")
print("=" * 80)

total_rows = 0

for slug, rows in sorted(duplicates.items()):
    print(f"\n{slug} ({len(rows)} rows)")
    print("-" * 80)

    for r in rows:
        total_rows += 1
        print(
            f"Category: {r['category_id']:>2} | "
            f"Name: {r['name']:<35} | "
            f"Icon: {r['icon']}"
        )

print("\n")
print("=" * 80)
print(f"Total Duplicate Rows : {total_rows}")
print("=" * 80)
