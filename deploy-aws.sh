#!/bin/bash

# AWS Elastic Beanstalk Deployment Script for NBCC Games Backend

set -e

echo "🚀 Starting AWS Elastic Beanstalk deployment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_NAME="nbcc-games-backend"
ENV_NAME="nbcc-games-prod"
REGION="us-east-1"
PLATFORM="python-3.11"

# Check if EB CLI is installed
if ! command -v eb &> /dev/null; then
    echo -e "${RED}❌ EB CLI not found. Installing...${NC}"
    pip install awsebcli
fi

# Check if AWS CLI is configured
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS CLI not configured. Please run: aws configure${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# Initialize EB if not already initialized
if [ ! -f ".elasticbeanstalk/config.yml" ]; then
    echo -e "${YELLOW}📦 Initializing Elastic Beanstalk application...${NC}"
    eb init -p $PLATFORM $APP_NAME --region $REGION
fi

# Check if environment exists
if ! eb list | grep -q $ENV_NAME; then
    echo -e "${YELLOW}🏗️  Creating new environment: $ENV_NAME${NC}"
    
    read -p "Do you want to create an RDS database? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        eb create $ENV_NAME \
            --instance-type t3.micro \
            --database.engine postgres \
            --database.username nbccadmin \
            --envvars DJANGO_SETTINGS_MODULE=nbcc_backend.settings
    else
        eb create $ENV_NAME \
            --instance-type t3.micro \
            --envvars DJANGO_SETTINGS_MODULE=nbcc_backend.settings
    fi
    
    echo -e "${GREEN}✅ Environment created successfully${NC}"
else
    echo -e "${GREEN}✅ Using existing environment: $ENV_NAME${NC}"
fi

# Set environment variables
echo -e "${YELLOW}🔧 Configuring environment variables...${NC}"

# Generate Django secret key if not set
if ! eb printenv | grep -q DJANGO_SECRET_KEY; then
    SECRET_KEY=$(python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    eb setenv DJANGO_SECRET_KEY="$SECRET_KEY"
fi

# Set other environment variables
eb setenv DJANGO_DEBUG="False"
eb setenv DJANGO_ALLOWED_HOSTS=".elasticbeanstalk.com"
eb setenv CORS_ALLOWED_ORIGINS="*"

echo -e "${GREEN}✅ Environment variables configured${NC}"

# Collect static files locally (optional)
echo -e "${YELLOW}📦 Collecting static files...${NC}"
python manage.py collectstatic --noinput --clear || true

# Deploy to Elastic Beanstalk
echo -e "${YELLOW}🚢 Deploying application to Elastic Beanstalk...${NC}"
eb deploy

# Check deployment status
echo -e "${YELLOW}📊 Checking deployment status...${NC}"
eb status

# Get the application URL
APP_URL=$(eb status | grep "CNAME" | awk '{print $2}')
echo -e "${GREEN}✅ Deployment complete!${NC}"
echo -e "${GREEN}🌐 Your application is available at: http://$APP_URL${NC}"

# Open logs
read -p "Do you want to view logs? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    eb logs
fi

echo -e "${GREEN}🎉 Deployment script completed successfully!${NC}"
