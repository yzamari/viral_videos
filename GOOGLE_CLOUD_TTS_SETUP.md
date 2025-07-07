# Google Cloud Text-to-Speech Setup Guide

## Overview

Google Cloud Text-to-Speech provides high-quality, natural-sounding voices with:
- **Neural2 Voices**: Advanced neural network voices
- **Journey Voices**: Most natural conversational voices
- **Studio Voices**: Premium broadcast-quality voices
- **Emotion Control**: Pitch and speed adjustments
- **SSML Support**: Advanced speech synthesis markup

## Prerequisites

1. **Google Cloud Account** with billing enabled
2. **Google Cloud Project** created
3. **gcloud CLI** installed

## Step-by-Step Setup

### Step 1: Enable Text-to-Speech API

```bash
# Enable the API
gcloud services enable texttospeech.googleapis.com

# Verify it's enabled
gcloud services list --enabled | grep texttospeech
```

### Step 2: Create Service Account

```bash
# Create service account for TTS
gcloud iam service-accounts create tts-service-account \
    --display-name="Text-to-Speech Service Account"

# Grant necessary permissions
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:tts-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudtts.client"

# Create and download credentials
gcloud iam service-accounts keys create ~/google-tts-key.json \
    --iam-account=tts-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com
```

### Step 3: Install Python Package

```bash
pip install google-cloud-texttospeech
```

### Step 4: Set Environment Variables

Add to your `.env` file:

```bash
# Google Cloud TTS Configuration
GOOGLE_APPLICATION_CREDENTIALS=/path/to/google-tts-key.json
GOOGLE_TTS_ENABLED=true
GOOGLE_TTS_VOICE_TYPE=en-US-Neural2-F  # Default voice
```

### Step 5: Test the Setup

```python
from google.cloud import texttospeech

# Test connection
client = texttospeech.TextToSpeechClient()

# List available voices
voices = client.list_voices()
print(f"Found {len(voices.voices)} voices")

# Test generation
synthesis_input = texttospeech.SynthesisInput(text="Hello, this is a test")
voice = texttospeech.VoiceSelectionParams(
    language_code="en-US",
    name="en-US-Neural2-F"
)
audio_config = texttospeech.AudioConfig(
    audio_encoding=texttospeech.AudioEncoding.MP3
)

response = client.synthesize_speech(
    input=synthesis_input,
    voice=voice,
    audio_config=audio_config
)

# Save test audio
with open("test_tts.mp3", "wb") as out:
    out.write(response.audio_content)
    print("✅ Test audio saved to test_tts.mp3")
```

## Available Voice Types

### Neural2 Voices (Recommended)
- **en-US-Neural2-A**: Female, warm tone
- **en-US-Neural2-C**: Female, young and energetic
- **en-US-Neural2-D**: Male, deep and authoritative
- **en-US-Neural2-F**: Female, mature and clear
- **en-US-Neural2-G**: Female, young and friendly
- **en-US-Neural2-H**: Female, confident
- **en-US-Neural2-I**: Male, young and casual
- **en-US-Neural2-J**: Male, mature and professional

### Journey Voices (Most Natural)
- **en-US-Journey-D**: Male, conversational
- **en-US-Journey-F**: Female, conversational

### Studio Voices (Premium Quality)
- **en-US-Studio-O**: Female, narrator quality
- **en-US-Studio-Q**: Male, narrator quality

## Voice Selection by Content Type

### Comedy/Funny Content
- Voice: `en-US-Neural2-C` (young, energetic)
- Pitch: +2.0
- Speed: 1.1x

### Serious/News Content
- Voice: `en-US-Neural2-D` (deep, authoritative)
- Pitch: -2.0
- Speed: 0.9x

### Exciting/Energetic Content
- Voice: `en-US-Neural2-G` (friendly, upbeat)
- Pitch: +4.0
- Speed: 1.2x

### Dramatic/Emotional Content
- Voice: `en-US-Studio-Q` (premium quality)
- Pitch: -1.0
- Speed: 0.85x

## SSML Support (Advanced)

For more control, use SSML:

```xml
<speak>
  <prosody rate="slow" pitch="-2st">
    This is serious news.
  </prosody>
  <break time="500ms"/>
  <prosody rate="fast" pitch="+2st">
    But wait, there's more!
  </prosody>
  <emphasis level="strong">This is important!</emphasis>
</speak>
```

## Pricing

- **Neural2 Voices**: ~$16 per 1 million characters
- **Journey Voices**: ~$16 per 1 million characters  
- **Studio Voices**: ~$160 per 1 million characters

Typical 60-second video script (~150 words, ~750 characters):
- Neural2/Journey: ~$0.012
- Studio: ~$0.12

## Quota and Limits

- **Characters per minute**: 1,000,000 (soft limit)
- **Requests per minute**: 1,000
- **Max input length**: 5,000 characters

## Troubleshooting

### Authentication Error
```bash
# Verify credentials are set
echo $GOOGLE_APPLICATION_CREDENTIALS

# Test authentication
gcloud auth application-default print-access-token
```

### API Not Enabled
```bash
# Enable the API
gcloud services enable texttospeech.googleapis.com
```

### Permission Denied
```bash
# Add Cloud TTS Client role
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:YOUR_SERVICE_ACCOUNT@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/cloudtts.client"
```

## Integration with Video Generator

The video generator automatically uses Google Cloud TTS when:
1. `GOOGLE_APPLICATION_CREDENTIALS` is set
2. The service account has proper permissions
3. The Text-to-Speech API is enabled

Fallback to basic gTTS happens automatically if Cloud TTS fails. 