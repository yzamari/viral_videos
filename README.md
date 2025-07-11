# 🎬 AI-Powered Viral Video Generator v2.2

**Enterprise-Ready Video Generation with Comprehensive Authentication Testing**

## 🔐 NEW: Authentication Testing

Before running the video generator, verify your Google Cloud authentication setup:

```bash
# Test all authentication methods
python check_auth.py

# Or test through main CLI
python main.py test-auth

# Generate video with authentication check (default)
python main.py generate --mission "your mission"

# Skip authentication test (not recommended)
python main.py generate --mission "your mission" --skip-auth-test
```

### 🧪 Authentication Tests Performed

The system automatically tests:

1. **gcloud CLI Authentication** - Verifies `gcloud auth login` status
2. **Application Default Credentials** - Tests ADC setup
3. **Service Account Authentication** - Validates service account JSON (if configured)
4. **Google AI Studio API** - Tests API key and model access
5. **Vertex AI API** - Verifies Vertex AI project and VEO model access
6. **Cloud Text-to-Speech API** - Tests TTS service access
7. **Cloud Storage Access** - Validates GCS bucket permissions
8. **Project & Billing** - Checks project configuration and billing status

## 🚀 Quick Start

### 1. Install Dependencies
```bash
git clone https://github.com/your-repo/viral-video-generator.git
cd viral-video-generator
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Authentication

#### Option A: Google Cloud SDK (Recommended)
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL

# Authenticate
gcloud auth login
gcloud auth application-default login
gcloud config set project YOUR_PROJECT_ID
```

#### Option B: Service Account
```bash
# Download service account JSON from Google Cloud Console
export GOOGLE_APPLICATION_CREDENTIALS="path/to/service-account.json"
```

### 3. Set API Keys
```bash
cp config.env.example config.env
# Edit config.env with your keys:
# GOOGLE_API_KEY=your_google_ai_studio_key
# VERTEX_AI_PROJECT_ID=your_project_id
```

### 4. Test Authentication
```bash
# Run comprehensive authentication test
python check_auth.py
```

### 5. Generate Videos
```bash
# Generate with frame continuity
python main.py generate --mission "Create engaging content about AI" --frame-continuity on

# Generate quick video
python main.py generate --mission "Explain quantum computing" --duration 15

# Generate with specific settings
python main.py generate \
  --mission "Teach people about renewable energy" \
  --platform youtube \
  --duration 30 \
  --style educational \
  --tone professional \
  --target-audience "students" \
  --frame-continuity auto
```

## 🔧 Authentication Setup Guide

### For Google AI Studio (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create an API key
3. Set `GOOGLE_API_KEY` in your environment

### For Vertex AI (Recommended for VEO)
1. Create a Google Cloud project
2. Enable Vertex AI API
3. Set up authentication:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```
4. Set environment variables:
   ```bash
   export VERTEX_AI_PROJECT_ID=your_project_id
   export VERTEX_AI_LOCATION=us-central1
   export VERTEX_AI_GCS_BUCKET=your_bucket_name
   ```

### For Cloud Text-to-Speech (Optional)
1. Enable Cloud Text-to-Speech API
2. Authentication is handled by ADC or service account

## 🎯 Features

### Core Features
- **🤖 AI-Powered Generation** - Uses Google's latest AI models
- **🎬 Frame Continuity** - Seamless video transitions with VEO2
- **🎭 Multi-Agent System** - 7+ AI agents for optimal content
- **📱 Platform Optimization** - YouTube, TikTok, Instagram support
- **🔐 Enterprise Authentication** - Comprehensive auth testing
- **📊 Session Management** - Organized file structure

### Advanced Features
- **🎨 Visual Style AI** - Intelligent style selection
- **🎤 Voice Director AI** - Optimal voice matching
- **📍 Positioning AI** - Smart subtitle placement
- **🔄 Error Recovery** - Robust fallback mechanisms
- **📈 Performance Monitoring** - Real-time metrics

## 📋 Command Reference

### Authentication Commands
```bash
# Test authentication
python main.py test-auth
python check_auth.py

# Generate with auth check (default)
python main.py generate --mission "your mission"

# Skip auth test (not recommended)
python main.py generate --mission "your mission" --skip-auth-test
```

### Generation Commands
```bash
# Basic generation
python main.py generate --mission "your mission"

# With frame continuity
python main.py generate --mission "your mission" --frame-continuity on

# Educational content
python main.py generate \
  --mission "Explain machine learning" \
  --category Educational \
  --style educational \
  --tone professional \
  --duration 45

# Social media optimized
python main.py generate \
  --mission "Viral dance trend" \
  --platform tiktok \
  --duration 15 \
  --style viral \
  --tone energetic
```

## 🔍 Troubleshooting

### Authentication Issues

#### "gcloud not found"
```bash
# Install Google Cloud SDK
curl https://sdk.cloud.google.com | bash
exec -l $SHELL
```

#### "No active gcloud accounts"
```bash
gcloud auth login
gcloud auth application-default login
```

#### "API key invalid"
- Check your Google AI Studio API key
- Verify the key has proper permissions
- Ensure sufficient quota

#### "Vertex AI access denied"
```bash
# Set correct project
gcloud config set project YOUR_PROJECT_ID

# Enable APIs
gcloud services enable aiplatform.googleapis.com
```

### Generation Issues

#### "Content policy violation"
- The system automatically rephrases violating prompts
- Check logs for specific violations
- Use more general, less specific language

#### "VEO quota exhausted"
- System automatically falls back to image generation
- Consider using Vertex AI for higher quotas
- Wait for quota reset (daily limits)

## 📊 Authentication Test Results

The authentication tester provides detailed results:

```
🔐 GOOGLE CLOUD AUTHENTICATION TEST REPORT
================================================================================

✅ Overall Status: SUCCESS
📊 Tests: 7 passed, 1 failed
🚀 Can run app: YES

📋 Individual Test Results:
----------------------------------------
✅ gcloud CLI Authentication: SUCCESS
✅ Application Default Credentials: SUCCESS
⏭️ Service Account Authentication: SKIPPED
✅ Google AI Studio API: SUCCESS
✅ Vertex AI API: SUCCESS
✅ Cloud Text-to-Speech API: SUCCESS
❌ Cloud Storage Access: FAILED
   Error: Bucket not found
   💡 Check bucket your-bucket-name exists and permissions are correct
✅ Project & Billing: SUCCESS

🚀 NEXT STEPS:
----------------------------------------
✅ All critical authentication tests passed!
🎬 You can now run the video generator:
   python main.py generate --mission 'your mission here'
```

## 🛡️ Security Best Practices

1. **Use Service Accounts** for production
2. **Rotate API Keys** regularly
3. **Limit API Key Scope** to required services only
4. **Monitor Usage** through Google Cloud Console
5. **Enable Billing Alerts** to prevent unexpected charges

## 🎯 Performance Optimization

- **Vertex AI**: Use for higher quotas and better performance
- **Frame Continuity**: Enable for narrative content, disable for quick cuts
- **Session Management**: Automatic cleanup of temporary files
- **Caching**: Intelligent caching of AI responses

## 📈 Monitoring

The system provides comprehensive monitoring:
- Authentication status
- API quota usage
- Generation performance
- Error rates and recovery
- Session organization

## 🤝 Contributing

1. Fork the repository
2. Run authentication tests: `python check_auth.py`
3. Create feature branch
4. Add tests for new features
5. Submit pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**🎬 Ready to create viral content? Start with `python check_auth.py` to verify your setup!**
