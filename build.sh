#!/usr/bin/env bash

# Exit immediately if any command fails.
set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔍 Running Django deployment checks..."
# Checks for production security issues.
python manage.py check --deploy --fail-level WARNING

echo "🗂 Collecting static files..."
# Copies all static files into STATIC_ROOT.
python manage.py collectstatic --noinput

echo "🛠 Running database migrations..."
# Applies pending migrations.
python manage.py migrate --noinput

# Uncomment only once when first deploying.
# echo "👤 Creating superuser..."
# python manage.py create_admin || true

# echo "🌍 Importing data (only first time)..."

# python manage.py import_countries || true
# python manage.py import_states || true
# python manage.py import_districts || true
# python manage.py import_subdistricts || true
# python manage.py import_villages || true
# python manage.py import_pincodes || true

echo "✅ Build completed successfully!"