# Next Steps for Your Viral Video Generator

## ✅ Fixed Issues

1. **Text Overlay Error**: Fixed the f-string formatting error that was causing "Unknown format code 'f'" errors
2. **Documentation**: Created comprehensive setup guides for Google Cloud services

## 🔧 What You Need to Do

### 1. Set Up Google Cloud Text-to-Speech (15 minutes)

Currently your videos use robotic gTTS voice. To get natural human voices:

1. **Go to Google Cloud Console**: https://console.cloud.google.com
2. **Create a new project** (or use existing one)
3. **Enable Text-to-Speech API**:
   ```bash
   gcloud services enable texttospeech.googleapis.com
   ```
4. **Create Service Account**:
   - Go to IAM & Admin → Service Accounts
   - Create new service account
   - Add role: "Cloud Text-to-Speech Client"
   - Download JSON key file
5. **Set Environment Variable**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your-key.json"
   ```
6. **Test it works**:
   ```bash
   python3 test_google_tts.py
   ```

### 2. Fix the Authentication Error

Your log shows: "503 Getting metadata from plugin failed with error: Reauthentication is needed"

This means you need to authenticate with Google Cloud:

```bash
# Option 1: Set service account credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/service-account-key.json"

# Option 2: Use gcloud auth
gcloud auth application-default login
```

### 3. Optional: Set Up Vertex AI for Real AI Images

If you want real AI-generated images instead of placeholders:

1. Enable Vertex AI API in Google Cloud Console
2. Add "Vertex AI User" role to your service account
3. Install the library:
   ```bash
   pip install google-cloud-aiplatform
   ```

## 💰 Cost Breakdown

- **Google Cloud TTS**: ~$0.01 per 60-second video
- **Vertex AI Imagen**: ~$0.60 per video (30 images)
- **Total**: Less than $1 per video with all premium features

## 🚀 Quick Test Commands

After setup, test everything works:

```bash
# Test with image-only mode (no VEO quota needed)
python3 main.py generate --topic "funny cats compilation" --image-only

# Test with Google TTS (after setup)
python3 test_google_tts.py

# Check your VEO quota
python3 main.py veo-quota
```

## 📚 Documentation

- **Google Console Setup**: See `GOOGLE_CONSOLE_SETUP_GUIDE.md`
- **TTS Setup**: See `GOOGLE_CLOUD_TTS_SETUP.md`
- **Complete Summary**: See `COMPLETE_SETUP_SUMMARY.md`

## 🎯 Priority

1. **Set up Google Cloud TTS** - Biggest improvement for minimal cost
2. **Fix authentication** - Required for TTS to work
3. **Optional: Vertex AI** - Only if you need photorealistic images

Your enhanced image placeholders already look great, so Vertex AI is optional!
