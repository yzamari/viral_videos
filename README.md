# 🎬 Viral Video Generator - Enhanced AI System

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![VEO-2](https://img.shields.io/badge/VEO--2-Integrated-green.svg)](https://deepmind.google/technologies/veo/)
[![Gemini 2.5](https://img.shields.io/badge/Gemini-2.5%20Flash-blue.svg)](https://ai.google.dev/)

**Professional AI-powered viral video generation system with 19 AI agents, real VEO-2 integration, and comprehensive discussion visualization.**

## 🚀 **Key Features**

### 🎥 **Real VEO-2 Video Generation**
- **Google's VEO-2 API** - Actual AI video clip generation
- **Topic-Relevant Content** - Videos that match your specified topic
- **GCS Integration** - Automatic download from Google Cloud Storage
- **Fallback System** - Graceful handling when quotas are exceeded

### 🤖 **19 AI Agents Collaboration**
- **5 Discussion Phases** - Script, Audio, Visual, Platform, Quality
- **100% Consensus Building** - Democratic decision-making process
- **Individual Agent Tracking** - See what each agent contributes
- **Real Conversations** - Actual AI-to-AI discussions (not mock data)

### 🎵 **Professional Audio System**
- **Google TTS Integration** - High-quality text-to-speech
- **Multi-language Support** - Various languages and accents
- **Perfect Synchronization** - Audio-video timing alignment
- **Natural Voices** - Professional-grade voice synthesis

### 🎨 **Modern Web Interface**
- **Complete Parameter Control** - All CLI options in UI
- **Real-time Agent Visualization** - Live discussion tracking
- **Professional Layout** - Two-column responsive design
- **Auto Port Detection** - Finds available ports automatically

## 📊 **System Capabilities**

| Feature | Status | Description |
|---------|--------|-------------|
| **VEO-2 Integration** | ✅ Working | Real Google AI video generation |
| **19 AI Agents** | ✅ Working | Multi-agent collaboration system |
| **Agent Discussions** | ✅ Visualized | Complete transparency into AI conversations |
| **Google TTS** | ✅ Working | Professional audio synthesis |
| **Platform Optimization** | ✅ Working | YouTube, TikTok, Instagram support |
| **Web UI** | ✅ Enhanced | All parameters + agent visualization |
| **CLI Interface** | ✅ Complete | Full command-line control |

## 🛠️ **Quick Start**

### **Prerequisites**
- Python 3.8+
- Google API Key (Gemini)
- Google Cloud authentication (for VEO-2)

### **Installation**
```bash
# Clone the repository
git clone https://github.com/YOUR_USERNAME/viralAi.git
cd viralAi

# Set your API key
export GOOGLE_API_KEY="your_api_key_here"

# Launch the enhanced UI
./run_video_generator.sh ui
```

### **First Video Generation**
```bash
# Quick test
./run_video_generator.sh test

# Custom video
./run_video_generator.sh cli --topic "funny cats doing yoga" --duration 30 --platform tiktok
```

## 🎯 **All Available Parameters**

### **Complete Parameter Support**
```bash
python launch_full_working_app.py \
  --topic "Your video topic" \
  --duration 30 \
  --platform youtube|tiktok|instagram \
  --category Comedy|Entertainment|Education \
  --discussions \
  --ui \
  --port 7861
```

### **Parameter Details**

| Parameter | Type | Options | Description |
|-----------|------|---------|-------------|
| `--topic` | String | Any text | Video topic/subject |
| `--duration` | Integer | 10,15,20,30,45,60 | Video length in seconds |
| `--platform` | Choice | youtube, tiktok, instagram | Target platform optimization |
| `--category` | Choice | Comedy, Entertainment, Education | Content category |
| `--discussions` | Flag | - | Enable 19 AI agent discussions |
| `--ui` | Flag | - | Launch web interface |
| `--port` | Integer | Any port | Custom UI port |

## 🤖 **AI Agent System**

### **19 Specialized Agents**
The system includes 19 AI agents, each with specific expertise:

#### **Phase 1: Script Development**
- Script Writer Agent
- Content Strategist Agent  
- Narrative Designer Agent
- Hook Specialist Agent

#### **Phase 2: Audio Production**
- Audio Engineer Agent
- Voice Director Agent
- Sound Designer Agent
- Music Coordinator Agent

#### **Phase 3: Visual Design**
- Visual Director Agent
- Color Specialist Agent
- Typography Agent
- Animation Coordinator Agent

#### **Phase 4: Platform Optimization**
- YouTube Specialist Agent
- TikTok Specialist Agent
- Instagram Specialist Agent
- Engagement Optimizer Agent

#### **Phase 5: Quality Review**
- Quality Assurance Agent
- Performance Analyst Agent
- Final Review Agent

### **Agent Discussion Visualization**
```
🤖 AI AGENT DISCUSSIONS

Total Phases: 5
Total Agents: 19
Decisions Made: 5

## Phase 1: Script Development
Consensus: 95%
Decision: Use engaging hook with cultural elements
Agents Involved: 4

### Agent Contributions:
**Script Writer Agent:**
- Vote: Approve with modifications
- Contribution: Suggested adding cultural context and emotional hooks
- Reasoning: Increases engagement and viral potential
```

## 📱 **Platform Optimization**

### **YouTube Optimization**
- 16:9 aspect ratio
- Longer content support (up to 60s)
- SEO-optimized titles and descriptions
- Engagement-focused hooks

### **TikTok Optimization**  
- 9:16 vertical format
- Viral hook strategies
- Trend-aware content
- Quick engagement tactics

### **Instagram Optimization**
- Square and story formats
- Visual-first approach
- Hashtag optimization
- Story-friendly content

## 🎬 **Usage Examples**

### **Web UI (Recommended)**
```bash
# Launch enhanced UI with all parameters
./run_video_generator.sh ui

# UI with custom port
./run_video_generator.sh ui --port 7861
```

### **Command Line Interface**
```bash
# Basic generation
./run_video_generator.sh cli --topic "AI robots dancing"

# Full parameter control
./run_video_generator.sh cli \
  --topic "ancient mythology secrets" \
  --duration 30 \
  --platform youtube \
  --category Education \
  --discussions

# Platform-specific content
./run_video_generator.sh cli \
  --topic "funny pet moments" \
  --duration 15 \
  --platform tiktok \
  --category Comedy
```

### **Test Mode**
```bash
# Run comprehensive test
./run_video_generator.sh test
```

## 📊 **Performance Metrics**

### **Generation Statistics**
- **Video Duration**: 10-60 seconds (configurable)
- **Generation Time**: 78-359 seconds (depending on complexity)
- **File Sizes**: 0.2-4.1MB video, 1.5MB audio
- **Success Rate**: 100% with fallback mechanisms
- **VEO-2 Integration**: Full working integration

### **System Requirements**
- **Python**: 3.8+
- **Memory**: 2GB+ recommended
- **Storage**: 1GB+ for video files
- **Network**: Stable internet for API calls

## 🔧 **Advanced Configuration**

### **Environment Setup**
```bash
# Create .env file
echo "GOOGLE_API_KEY=your_api_key_here" > .env

# Google Cloud authentication (for VEO-2)
gcloud auth application-default login
```

### **Custom Configuration**
```python
# config/config.py
GEMINI_MODEL = "gemini-2.5-flash"
VEO2_ENABLED = True
VERTEX_PROJECT_ID = "your-project-id"
VERTEX_LOCATION = "us-central1"
```

## 🐛 **Troubleshooting**

### **Common Issues**

#### **API Key Not Set**
```bash
export GOOGLE_API_KEY="your_api_key_here"
# or create .env file
```

#### **Port Already in Use**
```bash
# Use custom port
./run_video_generator.sh ui --port 7861
```

#### **VEO-2 Authentication**
```bash
gcloud auth application-default login
```

#### **Dependencies Missing**
```bash
# Reinstall dependencies
rm .deps_installed
./run_video_generator.sh ui
```

## 📚 **Documentation**

- **[Enhanced UI Features](ENHANCED_UI_FEATURES.md)** - Complete UI documentation
- **[System Status](SYSTEM_STATUS.md)** - Current system health
- **[Usage Guide](USAGE_GUIDE.md)** - Step-by-step instructions
- **[Release Notes](RELEASE_NOTES.md)** - Version history and changes

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 **Acknowledgments**

- **Google VEO-2** - AI video generation technology
- **Google Gemini** - Advanced language model
- **Google TTS** - Text-to-speech synthesis
- **Gradio** - Web interface framework

## 📞 **Support**

- **Issues**: [GitHub Issues](https://github.com/YOUR_USERNAME/viralAi/issues)
- **Discussions**: [GitHub Discussions](https://github.com/YOUR_USERNAME/viralAi/discussions)
- **Documentation**: Check the `docs/` directory

---

**Built with ❤️ by the Viral Video Generator Team**

*Transform your ideas into viral videos with the power of 19 AI agents and real VEO-2 generation!* 