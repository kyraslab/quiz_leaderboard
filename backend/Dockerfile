FROM python:3.11

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# Install system dependencies for database connection checking
RUN apt-get update && apt-get install -y netcat-openbsd && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY . .

# Create startup script directly in the image
RUN printf '#!/bin/bash\n\
echo "Waiting for database to be ready..."\n\
while ! nc -z db 5432; do\n\
  sleep 1\n\
done\n\
echo "Database is ready!"\n\
echo "Making migrations..."\n\
python manage.py makemigrations\n\
echo "Applying migrations..."\n\
python manage.py migrate\n\
echo "Populating data..."\n\
python manage.py populate_data --clear\n\
echo "Starting Django server..."\n\
exec "$@"\n' > /docker-entrypoint.sh && chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["gunicorn", "quiz_leaderboard.wsgi:application", "--bind", "0.0.0.0:8000"]
