#!/bin/sh
set -e

echo "Applying database migrations..."
python manage.py migrate --noinput

echo "Creating demo users..."
python manage.py create_demo_users || true

echo "Collecting static files..."
python manage.py collectstatic --noinput --clear || true

exec "$@"
