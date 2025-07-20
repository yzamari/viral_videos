# 🔐 Authentication Setup Guide

This guide explains how to set up authentication for the Viral AI Video Generator, including automatic authentication handling.

## 🚀 Quick Setup (Recommended)

### Option 1: Python Setup Script (Recommended)
```bash
python setup_env_with_auth.py
```

### Option 2: Shell Script
```bash
./setup_auth.sh
```

### Option 3: Quick Start (Includes Authentication)
```bash
./quick_start.sh
```

## 🔧 What the Authentication Setup Does

The automatic authentication system handles:

1. **Google Cloud SDK Installation Check**
   - Verifies `gcloud` CLI is installed
   - Provides installation instructions if missing

2. **Google Cloud Authentication**
   - Opens browser for Google account login
   - Sets up Application Default Credentials
   - Configures project settings

3. **API Enablement**
   - Enables Vertex AI API
   - Enables Text-to-Speech API
   - Enables Cloud Storage API
   - Enables Generative Language API

4. **Environment Configuration**
   - Creates/updates `.env` file
   - Sets correct project ID and location
   - Prompts for Google AI Studio API key

## 📋 Manual Setup (If Automatic Setup Fails)

### Step 1: Install Google Cloud SDK

**macOS (Homebrew):**
```bash
brew install google-cloud-sdk
```

**macOS (Manual):**
```bash
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

**Linux:**
```bash
# Add the Cloud SDK distribution URI
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee -a /etc/apt/sources.list.d/google-cloud-sdk.list

# Import the Google Cloud public key
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key --keyring /usr/share/keyrings/cloud.google.gpg add -

# Update and install
sudo apt-get update && sudo apt-get install google-cloud-cli
```

### Step 2: Authenticate with Google Cloud

```bash
# Login to Google Cloud
gcloud auth login

# Setup Application Default Credentials
gcloud auth application-default login

# Set project
gcloud config set project viralgen-464411
```

### Step 3: Enable Required APIs

```bash
gcloud services enable aiplatform.googleapis.com
gcloud services enable texttospeech.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable generativelanguage.googleapis.com
```

### Step 4: Create Environment File

Create a `.env` file in the project root:

```env
# Google Cloud Configuration
VERTEX_AI_PROJECT_ID=viralgen-464411
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_GCS_BUCKET=viral-veo2-results

# API Keys (Get from Google AI Studio)
GOOGLE_API_KEY=your_google_api_key_here
GEMINI_API_KEY=your_google_api_key_here

# Application Settings
LOG_LEVEL=INFO
SESSION_CLEANUP=true
```

### Step 5: Get Google AI Studio API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key and replace `your_google_api_key_here` in `.env`

## 🔍 Testing Authentication

Test your authentication setup:

```bash
python main.py test-auth
```

This will run comprehensive tests and show you exactly what's working and what needs to be fixed.

## 🤖 Automatic Authentication in Main App

The main application now automatically handles authentication problems:

1. **Detection**: When authentication fails, the app detects the specific issue
2. **Automatic Fix**: Opens `gcloud` authentication automatically
3. **Verification**: Re-tests authentication after fixing
4. **Graceful Fallback**: Continues with available services if some fail

### Example Usage:

```bash
# The app will automatically handle authentication
python main.py generate --mission "Create a funny video about cats" --platform tiktok

# Skip authentication test (not recommended)
python main.py generate --mission "Create a funny video about cats" --platform tiktok --skip-auth-test
```

## 🚨 Common Issues and Solutions

### Issue: "gcloud not found"
**Solution:** Install Google Cloud SDK using the instructions above.

### Issue: "API key not valid"
**Solution:** 
1. Get a new API key from [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Update the `GOOGLE_API_KEY` in your `.env` file

### Issue: "Quota exceeded"
**Solution:** 
1. Check your Google Cloud quotas
2. Request quota increases if needed
3. The app will automatically fall back to alternative methods

### Issue: "Permission denied"
**Solution:** 
1. Ensure you're logged into the correct Google account
2. Check that your account has access to the project
3. Re-run authentication: `gcloud auth login`

### Issue: "Project not found"
**Solution:** 
1. Verify the project ID is correct
2. Ensure you have access to the project
3. Set the project: `gcloud config set project viralgen-464411`

## 🔄 Re-running Authentication

If you need to re-authenticate:

```bash
# Clear existing authentication
gcloud auth revoke --all

# Re-run setup
python setup_env_with_auth.py
```

## 📊 Authentication Status Check

Check your current authentication status:

```bash
# Quick check
gcloud auth list

# Comprehensive check
python main.py test-auth
```

## 🎯 What Each Service Does

- **Vertex AI**: Powers VEO-2 video generation
- **Text-to-Speech**: Generates natural-sounding voice audio
- **Cloud Storage**: Stores generated videos and assets
- **Generative Language (Gemini)**: Powers AI agents and image generation
- **Google AI Studio**: Provides API access for Gemini models

## 🔐 Security Notes

- Your API keys are stored locally in `.env` file
- Never commit `.env` file to version control
- Application Default Credentials are stored securely by Google Cloud SDK
- All authentication is handled through official Google Cloud tools

## 💡 Tips

1. **First Time Setup**: Use the automatic setup script - it handles everything
2. **Development**: Use `--skip-auth-test` only for testing, not production
3. **Multiple Projects**: You can switch projects with `gcloud config set project PROJECT_ID`
4. **API Keys**: Keep your API keys secure and rotate them regularly

## 🆘 Getting Help

If you encounter issues:

1. Run the authentication test: `python main.py test-auth`
2. Check the error logs in `logs/` directory
3. Try the manual setup steps above
4. Ensure all required services are enabled in Google Cloud Console

The automatic authentication system is designed to handle most common scenarios, but manual setup is always available as a fallback. 