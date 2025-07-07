# 🚀 Enhanced Viral Video Generator - Running Instructions

## Quick Start (5 minutes)

```bash
# 1. Setup environment
git clone <repository-url>
cd viralAi
python3 -m venv .venv
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp config.env.example config.env
echo "GOOGLE_API_KEY=your_api_key_here" >> config.env

# 4. Generate your first video
python3 main.py generate --topic "AI creating amazing content" --duration 30

# 5. Launch web interface
python3 enhanced_ui.py
```

## 🎯 Command Line Usage

### Basic Video Generation

```bash
# Simple 30-second comedy video
python3 main.py generate --topic "Funny AI moments"

# Educational content
python3 main.py generate \
  --topic "How AI works" \
  --category Educational \
  --duration 45

# Tech news video
python3 main.py generate \
  --topic "Latest AI breakthroughs" \
  --category Tech \
  --platform youtube \
  --duration 60
```

### Advanced Options

```bash
# Deep AI discussions for high quality
python3 main.py generate \
  --topic "Future of artificial intelligence" \
  --duration 30 \
  --category Tech \
  --platform youtube \
  --discussions deep

# Quick generation with light discussions
python3 main.py generate \
  --topic "Quick AI tip" \
  --duration 15 \
  --discussions light

# Instagram-optimized video
python3 main.py generate \
  --topic "AI in daily life" \
  --duration 20 \
  --platform instagram \
  --category Entertainment
```

### All Available Parameters

```bash
python3 main.py generate \
  --topic "Your video topic" \
  --duration 30 \                    # 5-60 seconds
  --category Comedy \                # Comedy, Educational, Entertainment, News, Tech
  --platform youtube \               # youtube, tiktok, instagram, twitter
  --discussions standard             # light, standard, deep
```

## 🖥️ Web Interface Usage

### Launch Web UI

```bash
# Start the web interface
python3 enhanced_ui.py

# Access at: http://localhost:7860
# Features:
# - Interactive video generation
# - Real-time progress monitoring
# - Session history
# - Trending analysis
# - System status monitoring
```

### Web Interface Features

1. **Video Generation Tab**
   - Set topic, duration, category, platform
   - Choose discussion mode (light/standard/deep)
   -- Configure audio voice and emotion
   - Real-time progress with AI agent phases

2. **Monitoring & Analytics Tab**
   - View recent sessions
   - Agent performance statistics
   - System status and quotas

3. **Configuration Tab**
   - System settings overview
   - API key status
   - Performance configurations

## 🤖 AI Agent System

### Discussion Modes

```bash
# Light discussions (fast, 2-3 minutes)
--discussions light
# - Quick consensus building
# - Essential agents only
# - Faster generation

# Standard discussions (balanced, 4-5 minutes)
--discussions standard  # DEFAULT
# - Comprehensive agent participation
# - Good quality/speed balance
# - Recommended for most use cases

# Deep discussions (thorough, 6-8 minutes)
--discussions deep
# - All agents participate
# - Multiple discussion rounds
# - Highest quality output
```

### Agent Participation by Phase

1. **Planning Phase (4 agents)**
   - ExecutiveChief (Senior Manager)
   - SyncMaster, TrendMaster, StoryWeaver

2. **Script Phase (6 agents)**
   - ExecutiveChief, StoryWeaver, DialogueMaster
   - PaceMaster, TrendMaster, VisionCraft

3. **Visual Phase (4 agents)**
   - VisionCraft, PixelForge, StoryWeaver, SyncMaster

4. **Audio Phase (4 agents)**
   - AudioMaster, CutMaster, SyncMaster, StoryWeaver

5. **Assembly Phase (4 agents)**
   - CutMaster, SyncMaster, AudioMaster, PixelForge

## 📊 Output and Session Management

### Generated Files

```
outputs/
├── final_video_[session_id].mp4     # Your generated video
├── session_[session_id]/            # Session directory
│   ├── comprehensive_logs/          # Detailed logs
│   ├── agent_discussions/           # AI discussion reports
│   ├── enhanced_voice_[id].mp3      # Generated audio
│   └── session_summary.md           # Session overview
```

### Session Information

Each generation creates:
- **Video file**: `final_video_[session_id].mp4`
- **Session logs**: Comprehensive generation details
- **Discussion reports**: AI agent conversation summaries
- **Audio files**: Generated voice tracks
- **Metrics**: Performance and timing data

## 🎛️ Configuration Options

### Environment Configuration

Edit `config.env`:

```env
# Required
GOOGLE_API_KEY=your_google_ai_studio_key

# Optional - Google Cloud features
VEO_PROJECT_ID=your_google_cloud_project
VEO_LOCATION=us-central1
GOOGLE_TTS_ENABLED=true
GOOGLE_TTS_VOICE_TYPE=Neural2-F

# AI Agent settings
TOTAL_AI_AGENTS=26
DEFAULT_DISCUSSION_MODE=standard
MAX_DISCUSSION_ROUNDS=5
DISCUSSION_CONSENSUS_THRESHOLD=0.7
DISCUSSION_TIMEOUT_SECONDS=300

# Video/Audio quality
VIDEO_QUALITY=HD
AUDIO_QUALITY=high
CLEANUP_TEMP_FILES=true
```

### Voice and Audio Options

Available voice styles:
- **Neural2-F**: Female, natural voice
- **Neural2-D**: Male, deep voice  
- **Journey-F**: Female, conversational
- **Journey-D**: Male, conversational
- **Studio-O**: Female, narrator style
- **Studio-Q**: Male, narrator style

Audio emotions:
- **excited**: High energy, enthusiastic
- **funny**: Comedic timing, playful
- **serious**: Professional, authoritative
- **dramatic**: Intense, emotional
- **neutral**: Balanced, informative

## 🔧 Troubleshooting

### Common Issues and Solutions

1. **"ModuleNotFoundError"**
   ```bash
   # Ensure virtual environment is activated
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **"API key not found"**
   ```bash
   # Check config.env file exists and has your key
   cat config.env | grep GOOGLE_API_KEY
   ```

3. **"Permission denied"**
   ```bash
   # Make scripts executable
   chmod +x main.py enhanced_ui.py
   ```

4. **"Port already in use" (Web UI)**
   ```bash
   # Kill existing processes
   pkill -f "python3 enhanced_ui.py"
   # Or use different port
   python3 enhanced_ui.py --port 7861
   ```

5. **"Video generation failed"**
   ```bash
   # Check recent session logs
   ls -la outputs/session_*/comprehensive_logs/
   # Try with lighter discussions
   python3 main.py generate --topic "test" --discussions light
   ```

### Performance Optimization

**For faster generation:**
```bash
# Use light discussions
--discussions light

# Shorter videos
--duration 15

# Simple topics
--topic "Quick AI tip"
```

**For higher quality:**
```bash
# Use deep discussions
--discussions deep

# Longer videos for more content
--duration 45

# Complex topics
--topic "Comprehensive AI analysis"
```

### System Requirements

**Minimum:**
- Python 3.8+
- 4GB RAM
- 2GB free disk space
- Internet connection

**Recommended:**
- Python 3.10+
- 8GB RAM
- 5GB free disk space
- Fast internet connection

## 📈 Monitoring and Analytics

### Real-time Monitoring

Watch generation progress:
```bash
# Command line shows real-time updates
python3 main.py generate --topic "test" --duration 20

# Web interface provides visual progress
python3 enhanced_ui.py
```

### Session Analytics

Check recent sessions:
```bash
# List all sessions
ls outputs/session_*/

# View session summary
cat outputs/session_[id]/session_summary.md

# Check discussion reports
ls outputs/session_[id]/agent_discussions/
```

### Performance Metrics

Key metrics tracked:
- **Generation time**: Total time from start to finish
- **Discussion rounds**: Number of AI agent discussion cycles
- **Consensus levels**: Agreement percentage among agents
- **Agent participation**: Which agents contributed
- **Video quality**: File size, duration, format compliance

## 🚀 Production Deployment

### For Production Use

1. **Set up monitoring**
   ```bash
   # Log all generations
   python3 main.py generate --topic "prod video" 2>&1 | tee generation.log
   ```

2. **Batch processing**
   ```bash
   # Generate multiple videos
   for topic in "topic1" "topic2" "topic3"; do
     python3 main.py generate --topic "$topic" --duration 30
   done
   ```

3. **API integration**
   ```bash
   # Use as subprocess in your application
   import subprocess
   result = subprocess.run([
     "python3", "main.py", "generate",
     "--topic", "your topic",
     "--duration", "30"
   ])
   ```

## 🆘 Getting Help

### Debug Mode

```bash
# Enable verbose logging
export DEBUG=true
python3 main.py generate --topic "debug test"

# Check system status
python3 main.py status

# Validate configuration
python3 main.py validate-config
```

### Support Resources

- **Logs**: Check `outputs/session_*/comprehensive_logs/`
- **Documentation**: See `docs/` directory
- **Examples**: Working command examples above
- **Configuration**: Review `config.env.example`

### Common Success Patterns

```bash
# Successful 15-second comedy
python3 main.py generate \
  --topic "Funny AI assistant moments" \
  --duration 15 \
  --category Comedy \
  --discussions standard

# Successful educational content
python3 main.py generate \
  --topic "How machine learning works" \
  --duration 45 \
  --category Educational \
  --discussions deep

# Successful viral content
python3 main.py generate \
  --topic "AI technology breakthrough" \
  --duration 30 \
  --category Tech \
  --platform youtube \
  --discussions standard
```

---

**Ready to create viral content with 26+ AI agents! 🎬✨** 