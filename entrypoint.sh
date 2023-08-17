#!/bin/sh

python manage.py migrate auth --no-input
python manage.py migrate --no-input
python manage.py collectstatic --no-input --clear

gunicorn insta_backend.wsgi:application --bind 0.0.0.0:8000 & daphne -b 0.0.0.0 -p 8001 insta_backend.asgi:application
