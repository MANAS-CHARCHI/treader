#!/bin/ash
echo "Connected to Postgres"

python manage.py makemigrations
python manage.py migrate

exec "$@"