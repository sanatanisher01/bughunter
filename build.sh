#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Ensure database is ready
python manage.py makemigrations --no-input
python manage.py migrate --no-input

# Collect static files
python manage.py collectstatic --no-input