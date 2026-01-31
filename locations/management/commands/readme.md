# 🌍 Location Data Import Guide

This documentation outlines the process for importing Local Government Directory (LGD) geographic data into the TravelHub Django database. The import process is divided into 6 sequential scripts to handle dependencies and memory management efficiently.

## ✅ Prerequisites

Before running the scripts, ensure your environment is set up correctly.

### 1. Install Dependencies
You need pandas and openpyxl to read the Excel files.

```bash
pip install pandas openpyxl
```
# 2. Database Setup
Your database tables must exist before importing data. Run the migrations:

```bash
python manage.py makemigrations locations
python manage.py migrate
```

# 3. Folder Structure & Files
Create a folder named data in your project root. Place your LGD Excel files inside it with the exact filenames listed below:

```bash
your_project/
├── manage.py
├── locations/
│   └── management/
│       └── commands/      # Your 6 import scripts reside here
└── data/                  # Create this folder
    ├── All_States.xlsx
    ├── All_Districts.xlsx
    ├── All_SubDistricts.xlsx
    ├── All_Villages.xlsx  # (The large file ~600k rows)
    └── Pincode_Mapping.xlsx

```

⚠️ Important: Open each Excel file and delete any "Report Generated" metadata rows at the top. The first row must contain the column headers (e.g., State Code, Village Name).


# 🚀 Execution Guide (Strict Order)
You must run these commands in the exact order listed below. This is required because child records (like Districts) need their parent records (like States) to exist first to link the Foreign Keys.

## Step 1: Create Country
Initializes the root country "India".

```bash
python manage.py import_countries
```

## Step 2: Import States
Links States to the Country.

```bash
python manage.py import_states
```

## Step 3: Import Districts
Links Districts to their respective States.

```bash
python manage.py import_districts
```
## Step 4: Import Sub-Districts
Links Sub-Districts (Tehsils) to Districts.

```bash
python manage.py import_subdistricts
```
## Step 5: Import Villages (Bulk Operation)
Imports ~600,000+ villages.

## Note:

This process uses bulk_create to save data in chunks of 5,000.

Time: This may take 5–10 minutes depending on your CPU.

Progress: You will see a dot . printed for every batch processed.

```bash
python manage.py import_villages
```
(If you added Latitude/Longitude logic, they will be imported here)

## Step 6: Import Pincodes
Maps PIN codes to Villages.

```bash
python manage.py import_pincodes
```

## 🛠 Troubleshooting Common Errors

| Error Message | Cause | Solution |
|---------------|-------|----------|
| `FileNotFoundError: [Errno 2] No such file...` | The script cannot find the Excel file. | Check that the file is in the `data/` folder and the name matches exactly (case-sensitive). |
| `KeyError: 'State Code'` | The script cannot find the column header. | Open the Excel file. Ensure the first row contains the headers. If there is metadata above row 1, delete it. |
| `IntegrityError: NOT NULL constraint failed` | A required field is missing. | Ensure you are running the scripts in the correct order (1 → 6). |
| `ValueError: Field 'id' expected a number...` | Data type mismatch. | Ensure you updated your models to remove `_id` from field names (e.g., use `state = ForeignKey` instead of `state_id`). |

# 🔍 Verification
To confirm the data was imported successfully, open the Django shell:

```bash
python manage.py shell
```

Run these commands to check the counts:

```bash
python
from locations.models import State, District, Village

print(f"States: {State.objects.count()}")
print(f"Districts: {District.objects.count()}")
print(f"Villages: {Village.objects.count()}") 
# Expected Villages: > 600,000
```
