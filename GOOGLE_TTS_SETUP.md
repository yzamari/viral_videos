# Google Cloud Text-to-Speech Setup Guide

## 🎤 Why Google Cloud TTS?

Your videos currently use basic gTTS which sounds robotic. Google Cloud TTS offers:
- **Neural voices** that sound incredibly natural
- **Emotion control** (excited, serious, funny, etc.)
- **Speed & pitch** adjustments
- **Premium voices** like Journey and Studio quality

## 📋 Prerequisites

1. **Google Cloud Account** (free $300 credit for new users)
2. **Google Cloud Project** 
3. **Service Account Credentials**

## 🚀 Quick Setup (5 minutes)

### Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click **"Create Project"** or select existing project
3. Note your **Project ID** (you'll need this)

### Step 2: Enable Text-to-Speech API

```bash
# Option A: Using gcloud CLI
gcloud services enable texttospeech.googleapis.com

# Option B: Using Console UI
# Go to: https://console.cloud.google.com/apis/library/texttospeech.googleapis.com
# Click "Enable"
```

### Step 3: Create Service Account

1. Go to [Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click **"+ CREATE SERVICE ACCOUNT"**
3. Enter details:
   - Name: `viral-video-tts`
   - Description: `TTS for viral video generator`
4. Click **"CREATE AND CONTINUE"**
5. Grant role: **"Cloud Text-to-Speech User"**
6. Click **"DONE"**

### Step 4: Download Credentials

1. Click on the service account you created
2. Go to **"KEYS"** tab
3. Click **"ADD KEY"** → **"Create new key"**
4. Choose **JSON** format
5. Save the file as `google-tts-credentials.json`

### Step 5: Configure Your Environment

```bash
# Option 1: Set environment variable (temporary)
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/google-tts-credentials.json"

# Option 2: Add to .env file (permanent)
echo 'GOOGLE_TTS_CREDENTIALS="/path/to/google-tts-credentials.json"' >> .env

# Option 3: Copy to project directory
cp /path/to/google-tts-credentials.json viralAi/
```

### Step 6: Install Python Client

```bash
pip install google-cloud-texttospeech
```

## 🧪 Test Your Setup

Run this test script:

```python
from google.cloud import texttospeech

# Test connection
client = texttospeech.TextToSpeechClient()
print("✅ Google Cloud TTS connected successfully!")

# List available voices
voices = client.list_voices()
print(f"📢 Found {len(voices.voices)} available voices")
```

## 💰 Pricing

- **First 1 million characters/month**: FREE
- **Neural2 voices**: $16 per 1 million characters
- **Journey/Studio voices**: $160 per 1 million characters

For your use case (short viral videos), you'll likely stay within the free tier!

## 🎯 Integration with Viral Video Generator

Once setup is complete, the system will automatically use Google Cloud TTS instead of gTTS:

1. The system detects your credentials
2. Selects appropriate neural voice based on emotion
3. Falls back to gTTS only if Cloud TTS fails

### Voice Examples:

- **Funny**: Young female voice with higher pitch
- **Excited**: Energetic female voice with faster speed
- **Serious**: Deep male voice with slower pace
- **Dramatic**: Premium narrator voice
- **Neutral**: Natural conversational voice

## 🔧 Troubleshooting

### "Default credentials not found"
```bash
# Make sure credentials file exists and path is correct
ls -la /path/to/google-tts-credentials.json

# Verify environment variable
echo $GOOGLE_APPLICATION_CREDENTIALS
```

### "Permission denied"
- Check service account has "Cloud Text-to-Speech User" role
- Verify API is enabled in your project

### "Quota exceeded"
- Check usage at: https://console.cloud.google.com/apis/api/texttospeech.googleapis.com/quotas
- Consider implementing caching for repeated text

## 🎬 Ready to Generate!

Once setup, your videos will have natural, emotion-driven voices:

```bash
python generate_custom_video.py \
  --narrative dramatic \
  --feeling excited \
  --duration 15 \
  --realistic-audio \
  "Create an amazing video with natural voice"
```

The `--realistic-audio` flag activates Google Cloud TTS!
