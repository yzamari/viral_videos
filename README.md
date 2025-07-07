# 🎬 Enhanced Viral Video Generator v2.0

**Professional-grade viral video generation with 26+ AI agents and Senior Manager supervision**

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/yzamari/viral_videos.git
cd viral_videos
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Configure environment
cp config.env.example config.env
# Edit config.env with your API keys

# Generate a video
python3 main.py generate --topic "AI creating amazing content" --duration 30

# Launch web interface
python3 simple_test_ui.py
```

## ✨ Key Features

### 🤖 Advanced AI Agent System
- **26+ Specialized AI Agents** across 6 phases
- **Senior Manager (ExecutiveChief)** supervising all operations
- **Multi-phase discussions** with consensus building
- **Real-time agent visualization** and progress tracking

### 🎬 Professional Video Generation
- **VEO-2 Integration** for high-quality video generation
- **Google Cloud TTS** for natural audio with multiple voice styles
- **Multi-platform optimization** (YouTube, TikTok, Instagram)
- **Enhanced audio-visual synchronization**

### 📊 Comprehensive Monitoring
- **Real-time progress tracking** with detailed phase information
- **Session management** with organized file structure
- **Comprehensive logging** with metrics and analytics
- **Trending analysis** with configurable time ranges

### 🎛️ Multiple Interfaces
- **Command Line Interface** for automation and scripting
- **Web Interface** for interactive video generation
- **REST API** for integration with other systems

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Senior Manager AI                        │
│                   (ExecutiveChief)                          │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│              AI Agent Phases                               │
├─────────────────────┼───────────────────────────────────────┤
│ Script (4) → Audio (5) → Visual (6) → Platform (5) →      │
│ Quality (3) → Advanced (6)                                 │
└─────────────────────┼───────────────────────────────────────┘
                      │
┌─────────────────────┼───────────────────────────────────────┐
│              Video Generation Pipeline                     │
├─────────────────────┼───────────────────────────────────────┤
│ Script → VEO-2 → Audio → Assembly → Quality Check         │
└─────────────────────────────────────────────────────────────┘
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Google AI Studio API key
- Optional: Google Cloud credentials for enhanced features

### Environment Setup

1. **Clone Repository**
   ```bash
   git clone https://github.com/yzamari/viral_videos.git
   cd viral_videos
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment**
   ```bash
   cp config.env.example config.env
   ```
   
   Edit `config.env` with your settings:
   ```env
   GOOGLE_API_KEY=your_google_ai_studio_key
   VEO_PROJECT_ID=your_google_cloud_project
   VEO_LOCATION=us-central1
   GOOGLE_TTS_ENABLED=true
   ```

## 🎯 Usage Examples

### Command Line Interface

```bash
# Basic video generation
python3 main.py generate --topic "AI revolution" --duration 30

# Advanced options
python3 main.py generate \
  --topic "Future of AI technology" \
  --duration 45 \
  --category Tech \
  --platform youtube \
  --discussions deep

# Quick comedy video
python3 main.py generate \
  --topic "Funny AI moments" \
  --duration 15 \
  --category Comedy \
  --discussions light
```

### Web Interface

```bash
# Launch web UI
python3 simple_test_ui.py

# Access at http://localhost:7860
# Features:
# - Real-time progress monitoring
# - Comprehensive controls
# - Session history
# - Trending analysis
```

### Available Commands

```bash
# Generate video
python3 main.py generate [OPTIONS]

# List recent sessions
python3 main.py sessions

# Show system status
python3 main.py status

# Help
python3 main.py --help
```

## 🎛️ Configuration Options

### Video Generation Parameters
- `--topic`: Video topic/subject
- `--duration`: Video length (5-60 seconds)
- `--category`: Comedy, Educational, Entertainment, News, Tech
- `--platform`: youtube, tiktok, instagram, twitter
- `--discussions`: light, standard, deep

### AI Agent Configuration
- **Discussion Modes**: Control depth of AI agent discussions
- **Consensus Thresholds**: Minimum agreement levels
- **Timeout Settings**: Maximum discussion duration
- **Agent Participation**: Which agents participate in each phase

### Audio/Visual Settings
- **Voice Styles**: Neural2, Journey, Studio voices
- **Audio Emotions**: excited, funny, serious, dramatic, neutral
- **Video Quality**: HD, Full HD options
- **Platform Optimization**: Automatic aspect ratio and format selection

## 📊 AI Agent System

### Agent Phases

1. **Script Development (4 agents)**
   - StoryWeaver, DialogueMaster, PaceMaster, AudienceAdvocate

2. **Audio Production (5 agents)**
   - AudioMaster, VoiceDirector, SoundDesigner, NarrativeVoice, MoodMaster

3. **Visual Design (6 agents)**
   - VisionCraft, StyleDirector, ColorMaster, MotionExpert, CompositionGuru, PixelForge

4. **Platform Optimization (5 agents)**
   - PlatformGuru, EngagementHacker, AlgorithmWhisperer, TrendMaster, ViralityExpert

5. **Quality Assurance (3 agents)**
   - QualityGuard, AudienceAdvocate, AccessGuard

6. **Advanced Specialists (6 agents)**
   - DataMaven, MindReader, BrandMaster, SpeedDemon, InnovateMaster, SyncMaster

### Senior Manager Supervision
- **ExecutiveChief**: Strategic oversight across all phases
- **Real-time monitoring**: Continuous quality assessment
- **Resource optimization**: Efficient workflow coordination
- **Quality assurance**: Final approval and validation

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **API Key Issues**
   ```bash
   # Check config.env file
   cat config.env | grep GOOGLE_API_KEY
   ```

3. **Permission Errors**
   ```bash
   # Check file permissions
   chmod +x main.py
   ```

### Performance Optimization

- **Fast Generation**: Use `--discussions light`
- **High Quality**: Use `--discussions deep`
- **Balanced**: Use `--discussions standard` (default)

## 📁 Project Structure

```
viral_videos/
├── main.py                    # Main CLI interface
├── simple_test_ui.py         # Web interface
├── config/                    # Configuration management
├── src/
│   ├── agents/               # AI agent system
│   ├── generators/           # Video generation pipeline
│   ├── utils/               # Utilities and helpers
│   └── models/              # Data models
├── outputs/                  # Generated videos and sessions
├── docs/                    # Comprehensive documentation
└── requirements.txt         # Python dependencies
```

## 📚 Documentation

- **[System Architecture](docs/SYSTEM_ARCHITECTURE.md)** - Technical architecture details
- **[Workflow Guide](docs/WORKFLOW_GUIDE.md)** - Complete command reference
- **[AI Agents Guide](docs/AI_AGENTS_COMPLETE_GUIDE.md)** - Agent system documentation
- **[Features Verification](docs/FEATURES_VERIFICATION.md)** - Implementation status

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and feature requests
- **Discussions**: Community support and questions
- **Documentation**: Comprehensive guides and examples

---

**Built with ❤️ using 26+ AI Agents and Senior Manager supervision**
