# Vertex AI Imagen Setup Guide

## Prerequisites

1. **Google Cloud Account**: You need an active Google Cloud account with billing enabled
2. **Google Cloud Project**: Create or select a project
3. **APIs to Enable**:
   - Vertex AI API
   - Cloud Storage API (for image storage)

## Step 1: Install Google Cloud CLI

```bash
# macOS
brew install google-cloud-sdk

# Or download from: https://cloud.google.com/sdk/docs/install
```

## Step 2: Authenticate and Configure

```bash
# Login to Google Cloud
gcloud auth login

# Set application default credentials
gcloud auth application-default login

# Set your project
gcloud config set project YOUR_PROJECT_ID

# Enable required APIs
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
```

## Step 3: Install Required Python Packages

```bash
pip install google-cloud-aiplatform
pip install google-cloud-storage
```

## Step 4: Create a Cloud Storage Bucket (for generated images)

```bash
# Create a bucket for storing generated images
gsutil mb -p YOUR_PROJECT_ID gs://your-imagen-bucket-name/
```

## Step 5: Set Up Vertex AI Credentials

Create a service account and download the key:

```bash
# Create service account
gcloud iam service-accounts create imagen-service-account \
    --display-name="Imagen Service Account"

# Grant necessary roles
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
    --member="serviceAccount:imagen-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/aiplatform.user"

# Create and download key
gcloud iam service-accounts keys create ~/imagen-key.json \
    --iam-account=imagen-service-account@YOUR_PROJECT_ID.iam.gserviceaccount.com

# Set environment variable
export GOOGLE_APPLICATION_CREDENTIALS=~/imagen-key.json
```

## Step 6: Test Imagen Access

```python
from google.cloud import aiplatform

# Initialize
aiplatform.init(
    project="YOUR_PROJECT_ID",
    location="us-central1"
)

# Test Imagen
from vertexai.preview.vision_models import ImageGenerationModel

model = ImageGenerationModel.from_pretrained("imagen-3")
images = model.generate_images(
    prompt="A photorealistic B2 stealth bomber flying over desert",
    number_of_images=1,
    aspect_ratio="16:9",
    safety_filter_level="block_some",
    person_generation="allow_adult"
)

# Save image
images[0].save("test_imagen.jpg")
```

## Environment Variables for the Video Generator

Add these to your `.env` file:

```bash
# Vertex AI Configuration
VERTEX_AI_PROJECT_ID=your-project-id
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_BUCKET=gs://your-imagen-bucket-name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/imagen-key.json
ENABLE_VERTEX_AI_IMAGEN=true
```

## Quota and Pricing

- **Imagen 3 Pricing**: ~$0.020 per image (1024x1024)
- **Daily Quota**: Varies by project tier
- **Rate Limits**: 60 requests per minute (default)

## Troubleshooting

1. **Authentication Error**: Run `gcloud auth application-default login`
2. **API Not Enabled**: Check that Vertex AI API is enabled in Cloud Console
3. **Quota Exceeded**: Check your quotas in Cloud Console
4. **Region Issues**: Imagen may not be available in all regions, try us-central1 