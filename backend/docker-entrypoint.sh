#!/bin/bash

echo "Waiting for database to be ready..."
while ! nc -z db 5432; do
  sleep 1
done

echo "Database is ready!"

echo "Making migrations..."
python manage.py makemigrations

echo "Applying migrations..."
python manage.py migrate

if [ "$POPULATE_DATA" = "true" ]; then
  echo "Populating development data..."
  python manage.py populate_data --clear --users 1000 --sessions 2000
  
  echo "Warming up caches..."
  python manage.py warm_cache --all
fi

echo "Starting Django server..."
exec "$@"
