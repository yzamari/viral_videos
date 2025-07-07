# Final Setup Guide & Fixes Applied

## 🔧 Fixes Applied

### 1. Text Overlay Error Fixed ✅
**Error**: `Unknown format code 'f' for object of type 'str'`
**Cause**: Quadruple braces `{{{{` in f-string
**Fix**: Changed to double braces `{{` in AI prompt generation

### 2. Google TTS Authentication Issue
**Error**: `503 Getting metadata from plugin failed with error: Reauthentication is needed`
**Cause**: Missing Google Cloud credentials
**Status**: Falling back to basic gTTS (working)

## 📋 Google Cloud Console Setup Instructions

### Step 1: Access Google Cloud Console
1. Go to: https://console.cloud.google.com
2. Sign in with your Google account
3. If new to Google Cloud, you'll get $300 free credits

### Step 2: Create Project
1. Click project dropdown (top bar)
2. Click "NEW PROJECT"
3. Name: `viral-video-generator`
4. Click "CREATE"
5. Wait ~30 seconds for creation

### Step 3: Enable Billing
1. Go to: https://console.cloud.google.com/billing
2. Click "Link a billing account"
3. Add payment method (required even for free tier)

### Step 4: Enable APIs

#### For Text-to-Speech:
1. Go to: https://console.cloud.google.com/apis/library
2. Search: "Cloud Text-to-Speech API"
3. Click result → Click "ENABLE"
4. Wait for activation

#### For Image Generation (Vertex AI):
1. Search: "Vertex AI API" → Enable
2. Search: "Cloud Storage API" → Enable
3. Search: "Compute Engine API" → Enable

### Step 5: Create Service Account
1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "+ CREATE SERVICE ACCOUNT"
3. Fill in:
   - Name: `viral-video-service`
   - ID: `viral-video-service`
   - Description: `Service account for TTS and Imagen`
4. Click "CREATE AND CONTINUE"

### Step 6: Grant Permissions
1. Add these roles:
   - `Cloud Text-to-Speech User`
   - `Vertex AI User` (if using Imagen)
   - `Storage Object Admin` (if using Imagen)
2. Click "CONTINUE" → "DONE"

### Step 7: Create & Download Key
1. Click your service account name
2. Go to "KEYS" tab
3. Click "ADD KEY" → "Create new key"
4. Choose "JSON"
5. Click "CREATE"
6. **SAVE THE DOWNLOADED FILE!**

### Step 8: Set Up Authentication

#### macOS/Linux:
```bash
# Create secure directory
mkdir -p ~/.google-cloud-keys

# Move key file (adjust path to your download)
mv ~/Downloads/viral-video-*.json ~/.google-cloud-keys/service-key.json

# Set permissions
chmod 600 ~/.google-cloud-keys/service-key.json

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/.google-cloud-keys/service-key.json

# Add to shell profile for persistence
echo 'export GOOGLE_APPLICATION_CREDENTIALS=~/.google-cloud-keys/service-key.json' >> ~/.zshrc
```

#### Windows:
```powershell
# Create directory
mkdir C:\google-cloud-keys

# Move key file (adjust path)
move C:\Users\YourName\Downloads\viral-video-*.json C:\google-cloud-keys\service-key.json

# Set environment variable
setx GOOGLE_APPLICATION_CREDENTIALS "C:\google-cloud-keys\service-key.json"
```

### Step 9: Update .env File
```bash
# Google Cloud TTS
GOOGLE_APPLICATION_CREDENTIALS=/Users/YOUR_USERNAME/.google-cloud-keys/service-key.json
GOOGLE_TTS_ENABLED=true
GOOGLE_TTS_VOICE_TYPE=en-US-Neural2-F

# Google Cloud Project
GOOGLE_CLOUD_PROJECT=viral-video-generator

# Vertex AI (optional)
ENABLE_VERTEX_AI_IMAGEN=false
VERTEX_AI_PROJECT_ID=viral-video-generator
VERTEX_AI_LOCATION=us-central1
```

### Step 10: Test Setup
```bash
# Test TTS
python3 test_google_tts.py

# If successful, you'll see:
# ✅ Google Cloud TTS library imported successfully
# ✅ TTS client created successfully
# Lists of available voices
# Test audio files generated
```

## 💰 Pricing

### Text-to-Speech
- Neural2 Voices: $16 per 1M characters
- 60-second video: ~750 characters = $0.012
- 100 videos/month: ~$1.20

### Vertex AI Imagen (Optional)
- Imagen 3: $0.04 per image
- 30 images/video: $1.20
- 100 videos/month: ~$120

## 🚀 Quick Commands

### After Setup:
```bash
# Generate with natural voice
python3 main.py generate --topic "your topic" --image-only

# Check VEO quota
python3 main.py veo-quota

# Test specific voice
python3 test_google_tts.py
```

### Without Setup (Current):
```bash
# Works now with basic TTS
python3 main.py generate --topic "your topic" --image-only

# Works with enhanced placeholders
python3 main.py generate --topic "your topic" --fallback-only
```

## ❗ Common Issues

### 1. "API not enabled"
- Go to API Library
- Search for the API
- Click "ENABLE"

### 2. "Permission denied"
- Check service account roles
- Ensure all required roles added
- Re-download key if needed

### 3. "Reauthentication needed"
- Check GOOGLE_APPLICATION_CREDENTIALS path
- Verify key file exists
- Try: `gcloud auth application-default login`

### 4. "Billing account required"
- Must have billing enabled (even for free tier)
- Add payment method in billing section

## ✅ Current Status

### Working Now:
- ✅ Video generation with enhanced placeholders
- ✅ Basic gTTS audio (robotic but functional)
- ✅ Text overlay generation (f-string error fixed)
- ✅ Image-only mode with visual graphics

### After Google Cloud Setup:
- 🎤 Natural neural voices
- 🎨 Real AI images (optional)
- 💬 SSML emotion control
- 🔊 Multiple voice personalities

## 📞 Support Links

- [Google Cloud Console](https://console.cloud.google.com)
- [API Library](https://console.cloud.google.com/apis/library)
- [Billing Dashboard](https://console.cloud.google.com/billing)
- [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)

Remember: Everything works without Google Cloud setup - it just sounds better with it! 