#!/bin/bash

# Viral AI Video Generator - Authentication Setup Script
# This script automatically sets up Google Cloud authentication

set -e

echo "🚀 Viral AI Video Generator - Authentication Setup"
echo "=================================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local color=$1
    local message=$2
    echo -e "${color}${message}${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if gcloud is installed
if ! command_exists gcloud; then
    print_status $RED "❌ Google Cloud SDK not found"
    print_status $YELLOW "Installing Google Cloud SDK..."
    
    # Detect OS and install accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        if command_exists brew; then
            print_status $BLUE "Installing via Homebrew..."
            brew install google-cloud-sdk
        else
            print_status $RED "❌ Homebrew not found. Please install Google Cloud SDK manually:"
            print_status $BLUE "https://cloud.google.com/sdk/docs/install-sdk#mac"
            exit 1
        fi
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        # Linux
        print_status $BLUE "Installing Google Cloud SDK for Linux..."
        curl https://sdk.cloud.google.com | bash
        exec -l $SHELL
    else
        print_status $RED "❌ Unsupported OS. Please install Google Cloud SDK manually:"
        print_status $BLUE "https://cloud.google.com/sdk/docs/install"
        exit 1
    fi
else
    print_status $GREEN "✅ Google Cloud SDK found"
fi

# Check if already authenticated
if gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
    ACTIVE_ACCOUNT=$(gcloud auth list --filter=status:ACTIVE --format="value(account)")
    print_status $GREEN "✅ Already authenticated as: $ACTIVE_ACCOUNT"
else
    print_status $YELLOW "🔐 Google Cloud authentication required..."
    print_status $BLUE "Your browser will open for authentication"
    
    # Authenticate
    if gcloud auth login; then
        print_status $GREEN "✅ Authentication successful!"
    else
        print_status $RED "❌ Authentication failed"
        exit 1
    fi
fi

# Setup Application Default Credentials
print_status $BLUE "🔑 Setting up Application Default Credentials..."
if gcloud auth application-default print-access-token >/dev/null 2>&1; then
    print_status $GREEN "✅ Application Default Credentials already configured"
else
    print_status $YELLOW "Setting up Application Default Credentials..."
    print_status $BLUE "Your browser will open again for additional permissions"
    
    if gcloud auth application-default login; then
        print_status $GREEN "✅ Application Default Credentials configured!"
    else
        print_status $RED "❌ Failed to setup Application Default Credentials"
        exit 1
    fi
fi

# Set project
TARGET_PROJECT="viralgen-464411"
CURRENT_PROJECT=$(gcloud config get-value project 2>/dev/null || echo "")

if [[ "$CURRENT_PROJECT" != "$TARGET_PROJECT" ]]; then
    print_status $BLUE "🔧 Setting project to: $TARGET_PROJECT"
    if gcloud config set project $TARGET_PROJECT; then
        print_status $GREEN "✅ Project set successfully"
    else
        print_status $RED "❌ Failed to set project"
        exit 1
    fi
else
    print_status $GREEN "✅ Project already set: $TARGET_PROJECT"
fi

# Enable required APIs
print_status $BLUE "🔧 Enabling required APIs..."
APIS=(
    "aiplatform.googleapis.com"
    "texttospeech.googleapis.com"
    "storage.googleapis.com"
    "generativelanguage.googleapis.com"
)

for api in "${APIS[@]}"; do
    print_status $BLUE "Enabling $api..."
    if gcloud services enable $api; then
        print_status $GREEN "✅ Enabled $api"
    else
        print_status $YELLOW "⚠️ Failed to enable $api (may already be enabled)"
    fi
done

# Create/update .env file
print_status $BLUE "📝 Setting up environment file..."

if [[ ! -f ".env" ]]; then
    print_status $BLUE "Creating .env file..."
    cat > .env << EOF
# Viral AI Video Generator Environment Variables

# Google Cloud Configuration
VERTEX_AI_PROJECT_ID=$TARGET_PROJECT
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_GCS_BUCKET=viral-veo2-results

# API Keys (Get from Google AI Studio: https://makersuite.google.com/app/apikey)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# Application Settings
LOG_LEVEL=INFO
SESSION_CLEANUP=true
EOF
    print_status $GREEN "✅ Created .env file"
else
    print_status $GREEN "✅ .env file already exists"
    
    # Update project ID if needed
    if grep -q "VERTEX_AI_PROJECT_ID=" .env; then
        sed -i.bak "s/VERTEX_AI_PROJECT_ID=.*/VERTEX_AI_PROJECT_ID=$TARGET_PROJECT/" .env
        print_status $GREEN "✅ Updated project ID in .env file"
    fi
fi

# Check API key
if grep -q "GOOGLE_API_KEY=your_google_api_key_here" .env 2>/dev/null; then
    print_status $YELLOW "⚠️ Google API key needs to be configured"
    print_status $BLUE "Get your API key from: https://makersuite.google.com/app/apikey"
    print_status $BLUE "Then edit .env file and replace 'your_google_api_key_here' with your actual API key"
else
    print_status $GREEN "✅ API key appears to be configured"
fi

# Final test
print_status $BLUE "🧪 Running authentication test..."
if python -c "
import sys
sys.path.append('src')
from utils.gcloud_auth_tester import test_gcloud_authentication
result = test_gcloud_authentication()
success = result.get('analysis', {}).get('can_run_app', False)
print('SUCCESS' if success else 'PARTIAL')
" 2>/dev/null | grep -q "SUCCESS"; then
    print_status $GREEN "🎉 Authentication setup completed successfully!"
    print_status $GREEN "✅ You can now run: python main.py generate --help"
else
    print_status $YELLOW "⚠️ Setup completed with some limitations"
    print_status $BLUE "The app will work with fallback methods"
fi

echo "=================================================="
print_status $GREEN "🚀 Setup complete! Ready to generate viral videos!"
echo "==================================================" 