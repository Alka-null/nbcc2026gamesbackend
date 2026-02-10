"""
WSGI wrapper for Vercel deployment.
This file wraps the Django WSGI application for Vercel's serverless environment.
"""
import os
import sys
from pathlib import Path

# Add the project directory to the Python path
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))

# Set the Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'nbcc_backend.settings')

# Import the Django WSGI application
from django.core.wsgi import get_wsgi_application

# Create the WSGI application
application = get_wsgi_application()

# Vercel expects a variable named 'app'
app = application
