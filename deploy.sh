#!/bin/bash
# Post-deployment script to run migrations and seed data

echo "Running migrations..."
python manage.py migrate --noinput

echo "Seeding content (this will reset team members to exactly 3)..."
python manage.py seed_content --reset

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Deployment complete!"
