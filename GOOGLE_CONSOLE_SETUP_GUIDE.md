# Google Cloud Console Setup Guide

## Prerequisites
- Google account with billing enabled
- Credit card for billing (you get $300 free credits for new accounts)

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown at the top
   - Click "New Project"
   - Enter project name: `viral-video-generator`
   - Note your Project ID (you'll need this)
   - Click "Create"

3. **Enable Billing**
   - Go to: https://console.cloud.google.com/billing
   - Click "Link a billing account"
   - Follow prompts to add credit card
   - New users get $300 free credits

## Step 2: Enable Text-to-Speech API

1. **Navigate to APIs**
   - Go to: https://console.cloud.google.com/apis/library
   - Make sure your project is selected

2. **Search and Enable TTS**
   - Search for "Cloud Text-to-Speech API"
   - Click on it
   - Click "ENABLE" button
   - Wait for it to activate

3. **Verify API is Enabled**
   - Go to: https://console.cloud.google.com/apis/dashboard
   - You should see "Cloud Text-to-Speech API" in the list

## Step 3: Enable Vertex AI for Image Generation

1. **Enable Vertex AI API**
   - Go to: https://console.cloud.google.com/apis/library
   - Search for "Vertex AI API"
   - Click on it
   - Click "ENABLE" button

2. **Enable Additional Required APIs**
   - Also enable these APIs:
     - "Cloud Resource Manager API"
     - "Compute Engine API" (may auto-enable)
     - "Cloud Storage API" (for image storage)

## Step 4: Create Service Account

1. **Go to Service Accounts**
   - Navigate to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Make sure your project is selected

2. **Create Service Account**
   - Click "+ CREATE SERVICE ACCOUNT"
   - Service account details:
     - Name: `viral-video-service`
     - ID: `viral-video-service` (auto-fills)
     - Description: `Service account for TTS and Imagen`
   - Click "CREATE AND CONTINUE"

3. **Grant Permissions**
   - Add these roles:
     - `Cloud Text-to-Speech Client`
     - `Vertex AI User`
     - `Storage Object Admin` (for saving images)
   - Click "CONTINUE"
   - Click "DONE"

4. **Create JSON Key**
   - Click on your new service account
   - Go to "KEYS" tab
   - Click "ADD KEY" → "Create new key"
   - Choose "JSON" format
   - Click "CREATE"
   - **SAVE THIS FILE SECURELY** (downloads automatically)

## Step 5: Set Up Authentication

1. **Move Key File**
   ```bash
   # Create secure directory
   mkdir -p ~/.google-cloud-keys
   
   # Move downloaded key
   mv ~/Downloads/viral-video-*.json ~/.google-cloud-keys/service-key.json
   
   # Set permissions
   chmod 600 ~/.google-cloud-keys/service-key.json
   ```

2. **Set Environment Variable**
   ```bash
   # Add to ~/.zshrc or ~/.bash_profile
   export GOOGLE_APPLICATION_CREDENTIALS="$HOME/.google-cloud-keys/service-key.json"
   
   # Also add project ID
   export GOOGLE_CLOUD_PROJECT="your-project-id"
   
   # Reload shell
   source ~/.zshrc
   ```

## Step 6: Install gcloud CLI (Optional but Recommended)

1. **Download gcloud**
   - Go to: https://cloud.google.com/sdk/docs/install
   - Download for your OS
   - Run installer

2. **Initialize gcloud**
   ```bash
   gcloud init
   gcloud auth application-default login
   gcloud config set project YOUR_PROJECT_ID
   ```

## Step 7: Verify Setup

1. **Test Authentication**
   ```bash
   # Should show your project
   gcloud config get-value project
   
   # Should show enabled APIs
   gcloud services list --enabled
   ```

2. **Test with Python**
   ```bash
   # Run the test script
   python3 test_google_tts.py
   ```

## Cost Estimates

### Text-to-Speech Pricing
- **Neural2 Voices**: $16 per 1 million characters
- **Journey Voices**: $16 per 1 million characters
- **Studio Voices**: $160 per 1 million characters
- **Typical 60s video**: ~750 characters = $0.012

### Vertex AI Imagen Pricing
- **Image Generation**: $0.020 per image
- **Typical video (30 images)**: $0.60

### Monthly Estimates
- 100 videos/month with TTS: ~$1.20
- 100 videos/month with Imagen: ~$60
- Total: ~$61.20/month for 100 videos

## Troubleshooting

### "API not enabled" Error
```bash
# Enable via command line
gcloud services enable texttospeech.googleapis.com
gcloud services enable aiplatform.googleapis.com
```

### "Permission denied" Error
- Check service account has correct roles
- Verify GOOGLE_APPLICATION_CREDENTIALS is set
- Try: `gcloud auth application-default login`

### "Quota exceeded" Error
- Check quotas at: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/quotas
- Request quota increase if needed

## Quick Links

- **Google Cloud Console**: https://console.cloud.google.com
- **API Library**: https://console.cloud.google.com/apis/library
- **Service Accounts**: https://console.cloud.google.com/iam-admin/serviceaccounts
- **Billing**: https://console.cloud.google.com/billing
- **Quotas**: https://console.cloud.google.com/iam-admin/quotas

## Next Steps

1. Set up environment variables in your `.env` file:
   ```
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-key.json
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_TTS_ENABLED=true
   ENABLE_VERTEX_AI_IMAGEN=true
   ```

2. Install Python dependencies:
   ```bash
   pip install google-cloud-texttospeech google-cloud-aiplatform
   ```

3. Run test scripts to verify everything works! 