# 🎬 Veo-3 Setup Guide

## Overview

Veo-3 (`veo-3.0-generate-preview`) is Google's latest video generation model. It requires a different setup than Veo-2 because it uses Google Cloud Project configuration instead of just an API key.

## Why Veo-3 Isn't Showing Up

When using the standard API key approach:
```python
genai.configure(api_key=api_key)  # ❌ Won't show Veo-3
```

Veo-3 requires project-based configuration:
```python
genai.configure(
    project=PROJECT_ID,      # ✅ Shows Veo-3
    location=LOCATION
)
```

## Requirements for Veo-3

1. **Google Cloud Project**
   - Create at [console.cloud.google.com](https://console.cloud.google.com)
   - Note your Project ID

2. **Enable APIs**
   ```bash
   gcloud services enable aiplatform.googleapis.com
   gcloud services enable storage-api.googleapis.com
   ```

3. **Google Cloud Storage Bucket**
   - Veo-3 outputs directly to GCS
   - Create bucket: `gsutil mb gs://your-bucket-name`

4. **Authentication**
   ```bash
   gcloud auth application-default login
   ```

## Setup Steps

### 1. Install Google Cloud SDK
```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

### 2. Configure Project
```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Authenticate
gcloud auth application-default login
```

### 3. Set Environment Variables
```bash
# Add to .env
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_BUCKET=your-bucket-name
GOOGLE_CLOUD_LOCATION=us-central1
```

### 4. Install Additional Dependencies
```bash
pip install google-cloud-storage
```

## Using Veo-3 in Your Project

### Option 1: Use VertexVeo3Client
```python
from src.generators.vertex_veo3_client import VertexVeo3Client

# Initialize client
client = VertexVeo3Client(
    project_id="your-project-id",
    location="us-central1"
)

# Generate video to GCS
gcs_uri = client.generate_video_to_gcs(
    prompt="A majestic lion walking at sunset",
    output_gcs_uri="gs://your-bucket/videos/lion.mp4",
    duration_seconds=8
)

# Download to local
if gcs_uri:
    client.download_from_gcs(gcs_uri, "outputs/lion.mp4")
```

### Option 2: Direct API Usage
```python
import google.generativeai as genai

# Configure with project
genai.configure(
    project="your-project-id",
    location="us-central1"
)

# Use Veo-3
model = genai.GenerativeModel("veo-3.0-generate-preview")

# Generate video
generation_job = model.generate_content(
    ["A cinematic sunset over mountains", "gs://your-bucket/sunset.mp4"],
    generation_config={
        "video_length_sec": 8,
        "aspect_ratio": "16:9",
        "generate_audio": True,
    }
)
```

## Integrating with Viral Video Generator

To enable Veo-3 in the viral video generator:

1. **Set up Google Cloud** (steps above)

2. **Update .env**:
   ```
   GOOGLE_CLOUD_PROJECT=your-project-id
   GOOGLE_CLOUD_BUCKET=your-bucket-name
   USE_VEO3=true
   ```

3. **The system will automatically**:
   - Detect Veo-3 availability
   - Use it as first priority
   - Fall back to Veo-2 if needed

## Testing Veo-3 Setup

Run the test script:
```bash
python src/generators/vertex_veo3_client.py
```

Expected output:
```
✅ Veo-3 client initialized for project: your-project-id
```

## Troubleshooting

### "Veo-3 not detected"
- Ensure you're using project configuration, not just API key
- Check if Vertex AI API is enabled
- Verify authentication: `gcloud auth list`

### "Permission denied"
- Check IAM roles: need "Vertex AI User" role
- Verify bucket permissions

### "Model not found"
- Veo-3 might not be available in your region
- Try `us-central1` location

## Cost Considerations

- **Veo-3**: Charged per second of video generated
- **Storage**: GCS storage costs for output videos
- **Download**: Network egress charges

## Benefits of Veo-3

1. **Higher Quality**: Latest generation model
2. **Longer Videos**: Supports up to 8-second clips
3. **Better Motion**: Improved temporal consistency
4. **Audio Support**: Can generate synchronized audio
5. **Image Animation**: Can animate static images

## Summary

While Veo-3 requires more setup than Veo-2, it offers:
- Superior video quality
- More features (audio, image animation)
- Better motion and consistency

The viral video generator will automatically use Veo-3 when properly configured, giving you the best possible AI-generated videos! 