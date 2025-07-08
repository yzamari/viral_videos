# 🎬 Enhanced Viral Video Generator v2.0-RC3

**Production-ready viral video generation with AI agents and advanced composition**

## 🚀 Quick Start (5 Minutes)

### 1. Clone & Setup
```bash
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos
python3 -m venv .venv && source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Key
```bash
cp config.env.example config.env
# Edit config.env and add your Google AI Studio API key:
# GOOGLE_API_KEY=your_api_key_here
```
**Get your free API key**: [Google AI Studio](https://aistudio.google.com/)

### 3. Generate Your First Video
```bash
# Generate a quick test video
python3 main.py generate --topic "AI creating amazing content" --duration 30

# Or launch the web interface
python3 simple_test_ui.py
# Then visit: http://localhost:7860
```

## ✨ Key Features

### 🎯 **AI-Powered Topic Generation**
Transform high-level ideas into optimized video topics using 6 specialized AI agents:
```bash
# Generate topic from idea
python3 main.py generate-topic --idea "convince people to exercise more"

# Auto-generate video after topic creation
python3 main.py generate-topic --idea "promote sustainability" --generate-video
```

### 🤖 **Advanced Multi-Agent System**
- **26+ Specialized AI Agents** across 6 phases
- **Senior Manager Supervision** (ExecutiveChief) for strategic oversight
- **Real-time Consensus Building** with configurable discussion modes
- **100% Consensus Achievement** in latest testing

### 🎬 **Intelligent Video Composition**
- **AI-powered frame continuity decisions** (auto/on/off modes with 80-90% confidence)
- **VEO2 vs static image selection** per clip based on content analysis
- **Headers, titles, subtitles** with AI-optimized positioning and styling
- **Platform-specific optimization** (YouTube, TikTok, Instagram, Twitter)

### 📁 **Perfect Session Organization**
All files automatically organized in timestamped folders:
```
outputs/session_20250708_123456_abc123/
├── final_video_abc123.mp4           # Generated video
├── google_tts_voice_uuid.mp3        # Audio file
├── comprehensive_logs/              # System logs
├── agent_discussions/               # AI discussions
└── session_summary.md              # Human-readable summary
```

## 🌐 Web Interface

Launch the modern web interface:
```bash
python3 simple_test_ui.py
# Access at http://localhost:7860
```

**Features:**
- **🎯 Topic Generation Tab** - AI-powered topic creation with 6 agents
- **🎬 Video Generation Tab** - Complete video production with real-time progress
- **❓ Help Tab** - Comprehensive documentation and examples

## 📚 Documentation

- **[Setup Guide](docs/SETUP_GUIDE.md)** - Detailed installation and configuration
- **[Usage Guide](docs/USAGE_GUIDE.md)** - Complete feature documentation with examples
- **[Release Notes](RELEASE_NOTES.md)** - Latest v2.0-RC3 updates and features

## 🎯 Example Workflows

### 💡 Topic Generation → Video
```bash
# Transform idea into optimized topic, then generate video
python3 main.py generate-topic --idea "promote environmental awareness" --generate-video
```

### 🎬 Direct Video Generation
```bash
# Generate video with AI discussions and platform optimization
python3 main.py generate --topic "Quick fitness tips" --duration 30 --platform tiktok --discussions standard
```

### 🔧 Advanced Configuration
```bash
# Deep discussions for maximum quality
python3 main.py generate --topic "AI tutorial" --duration 60 --category Educational --platform youtube --discussions deep --frame-continuity auto
```

## 🤖 AI Agent System

### 🎯 **Topic Generation Agents (6)**
- **ContentStrategist**: Viral content strategy and audience engagement
- **PsychologyExpert**: Human psychology and persuasion techniques
- **EthicsAdvisor**: Content ethics and responsible messaging
- **PlatformSpecialist**: Social media platform optimization
- **TrendAnalyst**: Viral trends and content patterns
- **CommunicationExpert**: Effective messaging and storytelling

### 🎬 **Video Generation Agents (26+)**
- **Script Development**: StoryWeaver, DialogueMaster, PaceMaster
- **Visual Design**: VisionCraft, PixelForge, ColorMaster
- **Audio Production**: AudioMaster, VoiceCraft, SoundDesigner
- **Platform Optimization**: TrendMaster, ViralityExpert
- **Quality Assurance**: QualityGuard, CutMaster
- **Senior Management**: ExecutiveChief with strategic oversight

### 🗣️ **Discussion Modes**
- **Light**: 1-2 rounds, quick consensus, faster generation
- **Standard**: 2-3 rounds, balanced quality and speed
- **Deep**: 3-4 rounds, maximum quality and thorough analysis

## 🔧 Requirements

- **Python 3.8+** (Python 3.12 recommended)
- **Google AI Studio API Key** ([Get one free here](https://aistudio.google.com/))
- **4GB+ RAM** (recommended for complex videos)
- **Stable Internet** (for AI model access)
- **Optional**: Google Cloud account for enhanced Neural2 TTS

## 🚀 Production Ready Features

✅ **Comprehensive E2E Testing** - CLI and UI thoroughly verified  
✅ **Robust Error Handling** - Graceful fallback systems throughout  
✅ **Perfect Session Management** - 100% file organization success  
✅ **Complete Documentation** - Setup, usage, and troubleshooting guides  
✅ **Scalable Architecture** - Modular design for easy extension  
✅ **Clean Codebase** - Professional-grade code organization  

## 📊 Latest Release: v2.0-RC3

**🎉 Production Ready Release:**
- 📚 **Documentation Cleanup**: 59 → 5 essential files (91.5% reduction)
- 🎯 **AI-Powered Topic Generation**: 6 specialized agents with consensus building
- 🔧 **Critical Fixes**: VEO-2 warnings resolved, perfect session organization
- 🎨 **Enhanced UI**: Topic Generation tab with comprehensive controls
- 📁 **Clean Structure**: Professional repository organization

[📖 View Full Release Notes](RELEASE_NOTES.md)

## 🛠️ Troubleshooting

### Common Issues
- **Import errors**: Ensure virtual environment is activated
- **API errors**: Check your Google AI Studio API key in config.env
- **Permission errors**: Ensure write access to outputs/ directory

### Getting Help
1. Check console output for detailed error messages
2. Verify API key is valid: `python3 main.py veo-quota`
3. Review documentation: [Setup Guide](docs/SETUP_GUIDE.md)
4. Open GitHub issue for bugs or feature requests

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**🎬 Ready to create viral content with AI? Get started in 5 minutes!**

**Production deployment ready with comprehensive testing and documentation.**
