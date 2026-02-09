#!/bin/bash

# Azure App Service deployment script for Django

set -e

echo "Starting deployment..."

# Install Python dependencies
echo "Installing Python dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput

echo "Deployment completed successfully!"
