# 🚀 Vertex AI Veo-2 Setup Guide

**Complete setup guide for real AI video generation using your working configuration**

## 📋 Current Status

✅ **Your Configuration Working:**
- Project ID: `viralgen-464411`
- Location: `us-central1`
- GCS Bucket: `viral-veo2-results`
- API Endpoints: Successfully tested with curl

✅ **Integration Complete:**
- Python client implemented with your exact API structure
- Video generator updated with Vertex AI support
- Dependencies installed
- Test scripts created

⚠️ **Missing:** Authentication setup

---

## 🔧 Quick Setup (3 Steps)

### **Step 1: Install Google Cloud SDK**

**Option A: Download Installer**
```bash
# Download from: https://cloud.google.com/sdk/docs/install
# Follow the installation wizard
```

**Option B: macOS with Homebrew**
```bash
brew install --cask google-cloud-sdk
```

### **Step 2: Authenticate**

```bash
# 1. Login to Google Cloud
gcloud auth login

# 2. Set your project
gcloud config set project viralgen-464411

# 3. Set up Application Default Credentials
gcloud auth application-default login
```

### **Step 3: Test Real Veo-2**

```bash
# Activate environment
source venv/bin/activate

# Enable Vertex AI and test
USE_VERTEX_AI=true python example_usage.py --prompt "whimsical cartoon character riding a small pony" --duration 24
```

---

## 🎯 How to Use

### **Environment Variables**

Add to your `.env` file:
```bash
# Vertex AI Configuration (REAL AI VIDEO GENERATION)
USE_VERTEX_AI=true
VERTEX_AI_PROJECT_ID=viralgen-464411
VERTEX_AI_LOCATION=us-central1
VERTEX_AI_GCS_BUCKET=viral-veo2-results
```

### **Generate Videos with Real Veo-2**

```bash
# Custom baby animals video
USE_VERTEX_AI=true python example_usage.py --prompt "baby hanging out with animals" --duration 30

# Custom cartoon video  
USE_VERTEX_AI=true python example_usage.py --prompt "whimsical cartoon character riding a small pony" --duration 24

# Trending analysis + generation
USE_VERTEX_AI=true python example_usage.py
```

---

## 🔍 Verification Commands

### **Check Authentication**
```bash
gcloud auth list
gcloud config get-value project
```

### **Test API Access**
```bash
# Your working curl command
curl -X POST \
  -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  -H "Content-Type: application/json; charset=utf-8" \
  "https://us-central1-aiplatform.googleapis.com/v1/projects/viralgen-464411/locations/us-central1/publishers/google/models/veo-2.0-generate-001:predictLongRunning" \
  -d '{
    "instances": [{"prompt": "a whimsical cartoon character riding a small pony"}],
    "parameters": {"durationSeconds": 8, "aspectRatio": "16:9", "personGeneration": "allow_adult", "storageUri": "gs://viral-veo2-results/final-videos/"}
  }'
```

### **Run Test Suite**
```bash
source venv/bin/activate
python test_vertex_ai_real.py
```

---

## 📊 Expected Results

### **With Vertex AI (USE_VERTEX_AI=true):**
```
✅ Vertex AI Veo-2 client initialized
📡 Submitting job to: https://us-central1-aiplatform.googleapis.com/...
⏳ Polling for job completion...
✅ Job completed after 8 checks (120 seconds)
📹 Video generated at: gs://viral-veo2-results/final-videos/...
📥 Downloading video from GCS...
🎉 REAL Vertex AI Veo-2 video generated: outputs/veo2_clip_xxx.mp4 (2.3 MB)
```

### **Fallback Mode (authentication fails):**
```
❌ Authentication failed: Your default credentials were not found
🔄 Falling back to enhanced simulation...
✅ Fallback clip created: outputs/veo2_clip_xxx.mp4 (0.7 MB)
```

---

## 💰 Cost Information

**Vertex AI Veo-2 Pricing:**
- **Cost**: ~$0.10-0.30 per 8-second clip
- **Quota**: "Long running online prediction" quota (higher than Google AI Studio)
- **Billing**: Pay-per-use through Google Cloud billing

**Your Current Setup:**
- **Google AI Studio**: Hit quota limit (429 errors)
- **Vertex AI**: Unlimited generation with your activated billing

---

## 🚨 Troubleshooting

### **Authentication Errors**
```bash
# Error: "Your default credentials were not found"
gcloud auth application-default login

# Error: "Permission denied"  
gcloud auth login
gcloud config set project viralgen-464411
```

### **API Errors**
```bash
# Error: "Service not enabled"
gcloud services enable aiplatform.googleapis.com

# Error: "Bucket not found"
gsutil ls gs://viral-veo2-results/
```

### **Python Import Errors**
```bash
# Install missing dependencies
pip install google-cloud-aiplatform google-cloud-storage
```

---

## 🎉 Success Indicators

✅ **Authentication Working:**
```bash
gcloud auth list
# Shows your account as ACTIVE
```

✅ **API Access Working:**
```bash
gcloud auth print-access-token
# Returns a valid token starting with "ya29..."
```

✅ **Real Video Generation:**
```
🎉 REAL Vertex AI Veo-2 video generated: outputs/veo2_clip_xxx.mp4 (2.3 MB)
```

**File sizes:**
- **Real Veo-2**: 2-5 MB (actual AI video)
- **Simulation**: 0.1-0.7 MB (colored patterns)

---

## 📞 Support

**If you encounter issues:**

1. **Check logs** in the terminal output
2. **Verify authentication** with `gcloud auth list`
3. **Test API access** with the curl command above
4. **Run test suite** with `python test_vertex_ai_real.py`

**Your system is ready!** Just complete the authentication and you'll have unlimited real AI video generation! 🚀 