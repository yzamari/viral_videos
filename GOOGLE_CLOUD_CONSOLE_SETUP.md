# Google Cloud Console Setup Guide

## Prerequisites
- Google account with billing enabled
- Chrome/Firefox browser

## Step 1: Create Google Cloud Project

1. **Go to Google Cloud Console**
   - Navigate to: https://console.cloud.google.com
   - Sign in with your Google account

2. **Create New Project**
   - Click the project dropdown (top left)
   - Click "New Project"
   - Enter project name: `viralAi`
   - Click "Create"
   - Wait for project creation (~30 seconds)

3. **Enable Billing**
   - Go to: https://console.cloud.google.com/billing
   - Click "Link a billing account"
   - Follow prompts to add payment method
   - Note: You get $300 free credits for new accounts

## Step 2: Enable APIs

### Text-to-Speech API

1. **Navigate to API Library**
   - Go to: https://console.cloud.google.com/apis/library
   - Or click "APIs & Services" → "Library" in left menu

2. **Search and Enable TTS**
   - Search for: "Cloud Text-to-Speech API"
   - Click on the result
   - Click "ENABLE" button
   - Wait for activation (~1 minute)

### Vertex AI (for Imagen)

1. **Enable Vertex AI API**
   - In API Library, search: "Vertex AI API"
   - Click result and "ENABLE"
   
2. **Enable Additional APIs for Imagen**
   - Search and enable: "Cloud Storage API"
   - Search and enable: "Compute Engine API"
   - These are required for Vertex AI

## Step 3: Create Service Account

1. **Navigate to Service Accounts**
   - Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
   - Or click "IAM & Admin" → "Service Accounts"

2. **Create Service Account**
   - Click "+ CREATE SERVICE ACCOUNT"
   - Service account details:
     - Name: `viral-video-service`
     - ID: `viral-video-service` (auto-fills)
     - Description: `Service account for TTS and Imagen`
   - Click "CREATE AND CONTINUE"

3. **Grant Permissions**
   - Add these roles:
     - `Cloud Text-to-Speech User`
     - `Vertex AI User`
     - `Storage Object Admin` (for Imagen)
   - Click "CONTINUE"
   - Click "DONE"

## Step 4: Create and Download Keys

1. **Create JSON Key**
   - Click on your new service account
   - Go to "KEYS" tab
   - Click "ADD KEY" → "Create new key"
   - Select "JSON" format
   - Click "CREATE"
   - File downloads automatically (save it!)

2. **Secure Your Key**
   - Move downloaded file to safe location:
     ```bash
     mkdir -p ~/.google-cloud-keys
     mv ~/Downloads/viral-video-*.json ~/.google-cloud-keys/service-key.json
     chmod 600 ~/.google-cloud-keys/service-key.json
     ```

## Step 5: Set Environment Variables

Add to your `.env` file:

```bash
# Google Cloud Authentication
GOOGLE_APPLICATION_CREDENTIALS=/Users/YOUR_USERNAME/.google-cloud-keys/service-key.json

# Google Cloud Project
GOOGLE_CLOUD_PROJECT=viralAi

# Enable services
GOOGLE_TTS_ENABLED=true
ENABLE_VERTEX_AI_IMAGEN=true
VERTEX_AI_PROJECT_ID=viralAi
VERTEX_AI_LOCATION=us-central1
```

## Step 6: Verify Setup

### Test Text-to-Speech

```bash
# Run TTS test
python3 test_google_tts.py
```

Expected output:
- ✅ Google Cloud TTS library imported successfully
- ✅ TTS client created successfully
- Lists available voices
- Generates test audio files

### Test Vertex AI (Optional)

```bash
# Install Vertex AI SDK
pip install google-cloud-aiplatform

# Test connection
python3 -c "from google.cloud import aiplatform; print('Vertex AI ready')"
```

## Cost Estimates

### Text-to-Speech Pricing
- **Neural2 Voices**: $16 per 1 million characters
- **Journey Voices**: $16 per 1 million characters
- **Studio Voices**: $160 per 1 million characters
- **Typical 60s video**: ~750 characters = $0.012

### Vertex AI Imagen Pricing
- **Imagen 2**: $0.020 per image
- **Imagen 3**: $0.040 per image
- **Typical video (30 images)**: $0.60-$1.20

### Monthly Estimates
- 100 videos/month with TTS: ~$1.20
- 100 videos/month with Imagen: ~$60-120
- Total: ~$61-121/month for 100 videos

## Quotas and Limits

### Text-to-Speech
- 1,000,000 characters per minute
- 1,000 requests per minute
- 5,000 characters per request

### Vertex AI Imagen
- 100 requests per minute
- 1,000 images per day (soft limit)
- Can request increase through console

## Troubleshooting

### "API not enabled" Error
1. Go to: https://console.cloud.google.com/apis/dashboard
2. Check if APIs show as "Enabled"
3. If not, search in Library and enable

### "Permission denied" Error
1. Go to service account
2. Check roles include required permissions
3. Re-download JSON key if needed

### "Billing account not found"
1. Ensure billing is enabled
2. Check project is linked to billing account
3. Verify payment method is valid

## Quick Links

- **Console Home**: https://console.cloud.google.com
- **API Library**: https://console.cloud.google.com/apis/library
- **Service Accounts**: https://console.cloud.google.com/iam-admin/serviceaccounts
- **Billing**: https://console.cloud.google.com/billing
- **Quotas**: https://console.cloud.google.com/iam-admin/quotas

## Next Steps

1. After setup, test TTS with: `python3 test_google_tts.py`
2. Generate video with natural voice: `python3 main.py generate --topic "your topic"`
3. Monitor usage in console to track costs 