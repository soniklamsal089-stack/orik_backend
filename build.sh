#!/usr/bin/env bash
# Render runs this on every deploy. Any non-zero exit fails the build.
set -o errexit

pip install -r requirements.txt

# Collect admin + Jazzmin assets for WhiteNoise to serve.
python manage.py collectstatic --no-input

# Run database migrations
echo "==> Running database migrations..."
python manage.py migrate

# Initialize database with content (only if empty)
# This is safe to run on every deployment - it won't overwrite existing data
echo "==> Checking database initialization..."
python manage.py init_database

# Creates the admin login on first deploy if DJANGO_SUPERUSER_* are set.
echo "==> Ensuring superuser exists..."
python manage.py ensure_superuser

echo "==> Build complete!"
