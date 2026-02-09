#!/bin/bash

# Azure App Service startup script for Django with Daphne

# Run database migrations on startup
python manage.py migrate --noinput

# Start Daphne ASGI server
gunicorn nbcc_backend.wsgi:application --bind 0.0.0.0:8000 --workers 4 --timeout 600
