# 🎬 Enhanced Viral Video Generator v2.0

**Professional-grade viral video generation with AI agents and advanced composition**

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure (add your Google AI Studio API key)
cp config.env.example config.env

# Generate a video
python3 main.py generate --topic "AI creating amazing content" --duration 30

# Launch web interface
python3 simple_test_ui.py
```

## ✨ Key Features

### 🎯 **AI-Powered Topic Generation**
Transform high-level ideas into optimized video topics using 6 specialized AI agents:
```bash
python3 main.py generate-topic --idea "convince people to exercise more"
```

### 🤖 **Advanced Multi-Agent System**
- **26+ Specialized AI Agents** across 6 phases
- **Senior Manager Supervision** for strategic oversight
- **Real-time Consensus Building** with configurable discussion modes

### 🎬 **Intelligent Video Composition**
- **AI-powered frame continuity decisions** (auto/on/off modes)
- **VEO2 vs static image selection** per clip
- **Headers, titles, subtitles** with AI-optimized positioning
- **Platform-specific optimization** (YouTube, TikTok, Instagram, Twitter)

### 📁 **Perfect Session Organization**
All files automatically organized in timestamped folders:
```
outputs/session_20250708_123456_abc123/
├── final_video_abc123.mp4
├── google_tts_voice_uuid.mp3
├── comprehensive_logs/
└── agent_discussions/
```

## 🌐 Web Interface

Launch the modern web interface:
```bash
python3 simple_test_ui.py
# Access at http://localhost:7860
```

Features:
- **🎯 Topic Generation Tab** - AI-powered topic creation
- **🎬 Video Generation Tab** - Complete video production  
- **❓ Help Tab** - Comprehensive documentation

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Installation and configuration
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Complete feature documentation
- **[Release Notes](RELEASE_NOTES.md)** - Latest updates and features

## 🎯 Example Workflows

### Topic Generation → Video
```bash
# Generate optimized topic from idea
python3 main.py generate-topic --idea "promote environmental awareness" --generate-video
```

### Direct Video Generation
```bash
# Generate video with AI discussions
python3 main.py generate --topic "Quick fitness tips" --duration 30 --platform tiktok
```

## 🤖 AI Agent System

- **6 Topic Generation Agents**: ContentStrategist, PsychologyExpert, EthicsAdvisor, etc.
- **26+ Video Generation Agents**: Script, Visual, Audio, Assembly specialists
- **Discussion Modes**: Light (fast), Standard (balanced), Deep (quality)
- **Senior Manager**: ExecutiveChief provides strategic oversight

## 🔧 Requirements

- **Python 3.8+** (3.12 recommended)
- **Google AI Studio API Key** ([Get one here](https://aistudio.google.com/))
- **Optional**: Google Cloud account for enhanced TTS

## 🚀 Production Ready

✅ **Comprehensive Testing** - CLI and UI E2E verified  
✅ **Error Handling** - Robust fallback systems  
✅ **Session Management** - Perfect file organization  
✅ **Documentation** - Complete setup and usage guides  
✅ **Scalability** - Modular architecture for easy extension  

## 📊 Latest Release: v2.0-RC2

**New Features:**
- 🎯 AI-Powered Topic Generation with 6 specialized agents
- 🔧 Critical fixes for VEO-2 warnings and session organization
- 🎨 Enhanced UI with Topic Generation tab
- 📁 Perfect session folder organization (timestamped)

[View Full Release Notes](RELEASE_NOTES.md)

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎬 Ready to create viral content with AI? Get started in 5 minutes!**
