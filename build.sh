#!/usr/bin/env bash

set -o errexit

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🔍 Checking Django deployment..."
python manage.py check --deploy

echo "🗂 Collecting static files..."
python manage.py collectstatic --noinput

echo "🛠 Running migrations..."
python manage.py migrate --noinput

echo "👤 Creating superuser..."
python manage.py create_admin || true

echo "🌍 Importing data (only first time)..."

python manage.py import_countries || true
python manage.py import_states || true
python manage.py import_districts || true
python manage.py import_subdistricts || true
python manage.py import_villages || true
python manage.py import_pincodes || true

echo "✅ Build completed!"