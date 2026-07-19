# MasterSkill SQL Seeder Utilities

This document explains how to generate and validate MasterSkill SQL seed files.

These utilities provide:

- Auto-generated database `id`
- Auto-generated `masterskill_id` using ULID
- Auto-generated `created_at` and `updated_at`
- Duplicate skill name detection
- Duplicate skill slug detection

These commands are useful for importing large MasterSkill datasets into:

```
portfoliohub_masterskill
```

---

# 1. Requirements

Before using these commands, make sure:

- Django project is configured
- Database migrations are completed
- `generate_ulid_with_prefix()` utility exists
- Management commands are placed correctly


Example structure:

```
Life_hub
│
├── manage.py
│
├── portfoliohub
│   └── management
│       └── commands
│           │
│           ├── add_masterskill_fields.py
│           └── check_masterskill_duplicates.py
│
└── sql
    │
    ├── master_skills.sql
    └── master_skills_final.sql
```

---

# 2. ULID Generator

The command uses:

```python
from life_hub.utils import generate_ulid_with_prefix
```

Example:

```python
generate_ulid_with_prefix("msk")
```

Output:

```
msk_01JZ8X9K2V8A7M4Q1P3R5T6Y8
```

Format:

```
prefix + ULID
```

Example:

```
msk_xxxxxxxxxxxxxxxxxxxxxxxx
```

---

# 3. Raw MasterSkill SQL Format

The input SQL file should contain only original skill data.

Example file:

```
sql/master_skills.sql
```

Content:

```sql
INSERT INTO "public"."portfoliohub_masterskill"
(
    "category_id",
    "name",
    "slug",
    "icon",
    "description",
    "is_active",
    "priority"
)
VALUES

(
    1,
    'Python',
    'python',
    'fa-code',
    'General-purpose language known for readability and versatility.',
    true,
    1
),

(
    1,
    'JavaScript',
    'javascript',
    'fa-code',
    'Language used for frontend and backend development.',
    true,
    2
);
```

---

# 4. Generate IDs and Timestamps

Run this command from the Django project root:

Example location:

```
D:\Practical\Life_Hub\Life_hub
```

Command:

```bash
python manage.py add_masterskill_fields sql/master_skills.sql
```

---

## Custom Output File

Default output:

```
master_skills_updated.sql
```

Recommended:

```bash
python manage.py add_masterskill_fields \
sql/master_skills.sql \
--output sql/master_skills_final.sql
```

Generated file:

```
sql/master_skills_final.sql
```

---

# 5. Generated SQL Structure

The command converts:

```sql
(
1,
'Python',
'python',
'fa-code',
'description',
true,
1
)
```

into:

```sql
(
1,
'msk_01JZ8X9K2V8A7M4Q1P3R5T6Y8',
1,
'Python',
'python',
'fa-code',
'description',
true,
1,
CURRENT_TIMESTAMP,
CURRENT_TIMESTAMP
)
```

---

# Final Column Structure

Generated SQL:

```sql
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
```

---

# 6. Validate Duplicate Skills

Before importing into PostgreSQL, always check:

- Duplicate skill names
- Duplicate skill slugs


Command:

```bash
python manage.py check_masterskill_duplicates sql/master_skills_final.sql
```

---

# Duplicate Name Example

Output:

```
============================================================
DUPLICATE MASTER SKILL NAMES
============================================================


PYTHON (2 rows)

------------------------------------------------------------

ID : 10
MasterSkill ID : msk_01JZ8X91
Category : 1
Slug : python


ID : 50
MasterSkill ID : msk_01JZ8X92
Category : 2
Slug : python


Total Duplicate Name Rows : 2
```

---

# Duplicate Slug Example

Output:

```
============================================================
DUPLICATE MASTER SKILL SLUGS
============================================================


javascript (2 rows)

------------------------------------------------------------

ID : 20
MasterSkill ID : msk_01JZ8X99
Name : JavaScript


ID : 80
MasterSkill ID : msk_01JZ8XA0
Name : Javascript ES6


Total Duplicate Slug Rows : 2
```

---

# 7. Complete Workflow

Follow this order:

```
Create Raw SQL
        |
        |
        v
Generate IDs + ULID + Timestamps
        |
        |
        v
Check Duplicate Names/Slugs
        |
        |
        v
Fix Duplicate Records
        |
        |
        v
Import Into PostgreSQL
```

---

# 8. Full Example

## Step 1: Create SQL File

Location:

```
sql/master_skills.sql
```

---

## Step 2: Generate Final SQL

Run:

```bash
python manage.py add_masterskill_fields \
sql/master_skills.sql \
--output sql/master_skills_final.sql
```

Expected output:

```
Generated 200 rows.

Saved to sql/master_skills_final.sql
```

---

## Step 3: Validate Data

Run:

```bash
python manage.py check_masterskill_duplicates \
sql/master_skills_final.sql
```

Expected:

```
Duplicate Names : 0

Duplicate Slugs : 0
```

The SQL file is ready.

---

# 9. Import Into PostgreSQL

Using Django:

```bash
python manage.py dbshell < sql/master_skills_final.sql
```

Using PostgreSQL CLI:

```bash
psql database_name < sql/master_skills_final.sql
```

---

# 10. Recommended SQL Folder Structure

```
Life_hub
│
├── manage.py
│
├── portfoliohub
│
├── sql
│   │
│   ├── raw
│   │   │
│   │   └── master_skills.sql
│   │
│   └── generated
│       │
│       └── master_skills_final.sql
```

Recommended command:

```bash
python manage.py add_masterskill_fields \
sql/raw/master_skills.sql \
--output sql/generated/master_skills_final.sql
```

---

# 11. Best Practices

## Always validate before importing

Incorrect:

```
Generate SQL
      |
      v
Import Database
```


Correct:

```
Generate SQL
      |
      v
Check Duplicate Data
      |
      v
Import Database
```

---

## Keep Category IDs Fixed

Example:

```
1  Programming Languages
2  Frontend Development
3  Backend Development
4  Database
5  DevOps
6  AI / Data Science
```

Do not change category IDs after generating SQL.

---

## Use lowercase slugs

Recommended:

```
python
javascript
node-js
react-native
machine-learning
```

Avoid:

```
Python
JavaScript
NodeJS
```

---

# 12. Supported Dataset Size

These commands support:

```
100 skills
1,000 skills
10,000+ skills
```

No code changes are required.

---

# Summary

## Generate MasterSkill IDs

```bash
python manage.py add_masterskill_fields \
sql/master_skills.sql \
--output sql/master_skills_final.sql
```


## Check Duplicate Skills

```bash
python manage.py check_masterskill_duplicates \
sql/master_skills_final.sql
```


## Final Pipeline

```
Raw SQL
   |
   v
Generate ULID + IDs + Timestamps
   |
   v
Duplicate Validation
   |
   v
PostgreSQL Import
```