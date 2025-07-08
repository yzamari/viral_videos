# 🚀 Enhanced Viral Video Generator - Setup Guide

## 📋 Prerequisites

- **Python 3.8+** (3.12 recommended)
- **Google AI Studio API Key** (for Gemini models)
- **Google Cloud Account** (optional, for advanced TTS)
- **Git** for version control

## ⚡ Quick Setup (5 minutes)

### 1. Clone and Install
```bash
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp config.env.example config.env
# Edit config.env with your API keys
```

### 3. Test Installation
```bash
# Generate a quick test video
python3 main.py generate --topic "AI creating amazing content" --duration 10

# Launch web interface
python3 simple_test_ui.py
```

## 🔑 API Configuration

### Google AI Studio (Required)
1. Go to [Google AI Studio](https://aistudio.google.com/)
2. Create API key
3. Add to `config.env`:
```bash
GOOGLE_API_KEY=your_api_key_here
```

### Google Cloud TTS (Optional - Enhanced Audio)
1. Enable Cloud Text-to-Speech API
2. Create service account
3. Download JSON key
4. Add to `config.env`:
```bash
GOOGLE_APPLICATION_CREDENTIALS=path/to/service-account.json
```

## 🎬 Usage Examples

### CLI Commands
```bash
# Generate topic from idea
python3 main.py generate-topic --idea "convince people to exercise"

# Generate video
python3 main.py generate --topic "Quick fitness tips" --duration 30

# Auto-generate video from idea
python3 main.py generate-topic --idea "promote sustainability" --generate-video
```

### Web Interface
```bash
python3 simple_test_ui.py
# Access at http://localhost:7860
```

## 🔧 Troubleshooting

### Common Issues
- **Import errors**: Ensure virtual environment is activated
- **API errors**: Check API keys in config.env
- **Permission errors**: Ensure write access to outputs/ directory

### Getting Help
- Check the console output for detailed error messages
- Verify all dependencies are installed: `pip list`
- Ensure API keys are valid and have quota available

## 🎯 Advanced Configuration

### Discussion Modes
- **Light**: Quick consensus, faster generation
- **Standard**: Balanced discussion and quality  
- **Deep**: Thorough analysis, best quality

### Platform Optimization
- **YouTube**: Longer form, educational content
- **TikTok**: Short, viral, jump cuts
- **Instagram**: Visual focus, engagement
- **Twitter**: Concise, trending topics 