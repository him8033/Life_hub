```

Location Data Import DocumentationThis documentation provides instructions for importing the Local Government Directory (LGD) geographic data into the TravelHub Django database. The process is divided into 6 sequential parts to ensure data integrity and manage system memory effectively.🏗 Directory StructureBefore running the scripts, ensure your project structure looks like this:Plaintextyour_project/
├── manage.py
├── data/                  # Create this folder
│   ├── All_States.xlsx
│   ├── All_Districts.xlsx
│   ├── All_SubDistricts.xlsx
│   ├── All_Villages.xlsx
│   └── Pincode_Mapping.xlsx
└── locations/
    └── management/
        └── commands/      # All 6 scripts go here
⚙️ PrerequisitesClean Excel Files: Ensure that the first row of every Excel file contains the headers. Delete any metadata rows (like "Report Date") at the top of the LGD exports.Database Migrations: Your tables must exist before importing.Bashpython manage.py makemigrations locations
python manage.py migrate
Required Libraries:Bashpip install pandas openpyxl
🚀 Execution OrderThe data is hierarchical. You must run these commands in the specific order listed below because each level depends on the ID of the parent level.Part 1: CountryInitializes India as the root country (ID: 1).Bashpython manage.py import_countries
Part 2: StatesMaps states to the country.Bashpython manage.py import_states
Part 3: DistrictsMaps districts to their respective states.Bashpython manage.py import_districts
Part 4: Sub-DistrictsMaps sub-districts (Tehsils/Talukas) to districts.Bashpython manage.py import_subdistricts
Part 5: Villages (Large Data)Imports ~600,000 villages. This script uses Bulk Processing to prevent memory crashes. It will display a progress dot . for every 5,000 records processed.Bashpython manage.py import_villages
Part 6: PincodesMaps PIN codes to specific villages.Bashpython manage.py import_pincodes
🛠 Features of the Import ScriptsError Tolerance: Each script contains try-except blocks. If one row in the Excel is corrupt, the script logs the error and continues to the next row instead of crashing.Empty Field Handling: The scripts use pd.isna() to detect empty cells. Rows with missing primary IDs or names are skipped automatically.Duplicate Prevention: Uses update_or_create for small sets and ignore_conflicts=True for bulk sets. You can run these scripts multiple times without creating duplicate data.Automatic Slugs: All names are converted to URL-friendly slugs (e.g., New Delhi becomes new-delhi).⚠️ TroubleshootingIssueSolutionFile Not FoundEnsure the file is inside the data/ folder and the filename matches exactly.Column Not FoundOpen your Excel and verify the header name matches the script (e.g., "Village Code").Out of MemoryThe Village and Pincode scripts are optimized, but ensure you have at least 2GB of free RAM.IntegrityErrorEnsure you ran the scripts in order (1 to 6). You cannot import a District if the State doesn't exist yet.📊 VerificationAfter running all scripts, you can verify the count in your Django shell:Bashpython manage.py shell
Pythonfrom locations.models import Village
print(Village.objects.count()) # Should be approximately 600,000+