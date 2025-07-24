#!/bin/bash

echo "Waiting for database to be ready..."
until python -c "
import psycopg2
import os
import sys
try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'db'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        dbname=os.getenv('DB_NAME'),
        connect_timeout=10
    )
    conn.close()
    print('Database connection successful!')
except Exception as e:
    print(f'Database not ready: {e}')
    sys.exit(1)
"; do
  echo "Database not ready, waiting..."
  sleep 2
done

echo "Database is ready!"

echo "Making migrations..."
python manage.py makemigrations
if [ $? -ne 0 ]; then
  echo "Error: Failed to make migrations"
  exit 1
fi

echo "Applying migrations..."
python manage.py migrate
if [ $? -ne 0 ]; then
  echo "Error: Failed to apply migrations"
  exit 1
fi

if [ "$POPULATE_DATA" = "true" ]; then
  echo "Populating development data..."
  python manage.py populate_data --clear --users 1000 --sessions 20000
  if [ $? -ne 0 ]; then
    echo "Error: Failed to populate data"
    exit 1
  fi
fi

echo "Starting Django server..."
exec "$@"
