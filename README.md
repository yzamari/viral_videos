# ViralAI - AI-Powered Video Generation System

🚀 **Advanced AI video generation system with 22 specialized agents, centralized decision-making, and comprehensive social media integration.**

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Google AI API key

### Installation
```bash
git clone <repository-url>
cd viralAi
pip install -r requirements.txt
```

### Authentication Setup
```bash
# The system will automatically configure authentication
python main.py generate --mission "Test video" --platform instagram --duration 10
```

### Basic Usage
```bash
# Generate a professional video with 22 AI agents
python main.py generate \
  --mission "Teach kids about recycling" \
  --platform instagram \
  --duration 15 \
  --mode professional

# Generate with specific style and tone
python main.py generate \
  --mission "Promote healthy eating habits" \
  --platform tiktok \
  --duration 30 \
  --style viral \
  --tone engaging \
  --visual-style dynamic

# Cost-effective testing mode
python main.py generate \
  --mission "Test content creation" \
  --platform youtube \
  --duration 20 \
  --cheap full
```

## Key Features

### 🎯 **Centralized Decision Framework**
- All decisions made upfront before generation
- No conflicting parameters between components
- Complete traceability of decision sources
- Consistent results across all components

### 🤖 **22 AI Agents System**
- **Professional Mode**: 22 specialized agents
- **Enhanced Mode**: 7 core agents  
- **Simple Mode**: Minimal AI for fast generation
- Consensus-based collaboration
- Platform-specific optimizations

### 🎬 **Advanced Video Generation**
- **VEO-2**: Google's latest video generation model
- **VEO-3**: Premium model with native audio
- **Fallback**: FFmpeg-based generation for testing
- Frame continuity for seamless transitions
- Precise duration control

### 🎵 **Intelligent Audio**
- AI-powered voice selection
- Enhanced multilingual TTS
- Voice strategy optimization
- Perfect audio-video synchronization

### 📱 **Social Media Integration**
- Auto-posting to Instagram, TikTok, YouTube
- AI-generated trending hashtags
- Platform-specific optimization
- Engagement tracking

### 💰 **Cost Management**
- **Cheap Mode**: Cost-effective testing
- **Granular Levels**: Full/Audio/Video cheap modes
- **Fallback Systems**: Automatic cost reduction
- **Quota Management**: Smart resource usage

## System Architecture

### Decision-First Architecture
```
CLI Input → Decision Framework → Core Decisions → All Components
```

### AI Agent Discussions
```
22 Agents → 7 Discussion Topics → Consensus → Strategy Implementation
```

### Generation Pipeline
```
Decisions → Discussions → Scripts → Video/Audio → Assembly → Social Media
```

## Command Line Options

### Required Parameters
- `--mission` - Video mission/topic (e.g., "Teach about climate change")
- `--platform` - Target platform (instagram, tiktok, youtube, twitter, linkedin)

### Optional Parameters
- `--duration` - Video duration in seconds (default: 20)
- `--mode` - Generation mode (simple/enhanced/professional, default: enhanced)
- `--style` - Content style (viral/educational/professional, default: viral)
- `--tone` - Content tone (engaging/professional/humorous, default: engaging)
- `--visual-style` - Visual style (dynamic/minimalist/cinematic, default: dynamic)
- `--category` - Content category (Comedy/Educational/Entertainment/News/Tech)
- `--target-audience` - Target audience description
- `--cheap` - Cheap mode level (full/audio/video/off, default: off)
- `--no-cheap` - Disable cheap mode
- `--frame-continuity` - Enable frame continuity (on/off/auto, default: auto)

## Generation Modes

### Simple Mode
- Basic generation with minimal AI
- Fastest generation time
- Lowest cost
- Good for testing

### Enhanced Mode (Default)
- 7 AI agents with discussions
- Balanced performance and quality
- Moderate cost
- Recommended for most use cases

### Professional Mode
- 22 AI agents with comprehensive discussions
- Highest quality and optimization
- Premium cost
- Best for production content

## Platform Support

### Instagram
- 9:16 aspect ratio
- 15-90 second duration
- Auto-posting with hashtags
- Stories and Reels optimization

### TikTok
- 9:16 aspect ratio
- 15-60 second duration
- Trend-based optimization
- Hashtag strategy

### YouTube
- 16:9 aspect ratio
- 15-300 second duration
- SEO optimization
- Thumbnail generation

### Twitter
- 16:9 aspect ratio
- 15-140 second duration
- Character-limited captions
- Engagement optimization

### LinkedIn
- 16:9 aspect ratio
- 15-300 second duration
- Professional tone adaptation
- Business-focused content

## Session Management

Every generation creates a session with complete tracking:

```
outputs/session_YYYYMMDD_HHMMSS/
├── decisions/           # All decisions made
├── discussions/         # AI agent discussions
├── scripts/            # Script versions
├── audio/              # Audio files
├── video_clips/        # Generated clips
├── final_output/       # Final video
├── hashtags/           # Generated hashtags
├── logs/               # Comprehensive logs
└── metadata/           # Session metadata
```

## Configuration

### Environment Variables
```bash
export GOOGLE_AI_API_KEY="your-gemini-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project"
```

### Configuration Files
- `config.json` - User preferences
- `CLAUDE.md` - System instructions
- Platform-specific settings

## Cost Optimization

### Cheap Mode Options
```bash
# Full cheap mode - text video + gTTS audio
python main.py generate --mission "Test" --cheap full

# Audio cheap mode - normal video + gTTS audio  
python main.py generate --mission "Test" --cheap audio

# Video cheap mode - fallback video + normal audio
python main.py generate --mission "Test" --cheap video
```

### Resource Management
- Automatic fallback on quota exceeded
- Smart retry logic
- Cost tracking and reporting
- Batch processing optimization

## Monitoring & Debugging

### Comprehensive Logging
- Decision traceability
- AI agent discussions
- Generation pipeline tracking
- Performance metrics

### Session Analysis
- Complete audit trail
- Error debugging
- Performance analysis
- Cost tracking

## Security & Privacy

### Authentication
- Google Cloud IAM integration
- Secure API key management
- Auto-authentication setup

### Data Protection
- No sensitive data in logs
- Secure credential storage
- Session-based file organization

## Troubleshooting

### Common Issues
1. **Authentication Problems**: Run any command - system auto-fixes
2. **Quota Exceeded**: Use `--cheap full` for testing
3. **Duration Conflicts**: All resolved with centralized decisions
4. **VEO Unavailable**: Automatic fallback to alternative generation

### Getting Help
- Check `logs/` directory for detailed error information
- Review session files for debugging
- Use `--cheap full` for cost-effective testing

## Advanced Usage

### Custom Workflows
```bash
# Educational content with specific targeting
python main.py generate \
  --mission "Explain photosynthesis to middle school students" \
  --platform youtube \
  --duration 60 \
  --style educational \
  --tone engaging \
  --target-audience "middle school students"

# Marketing content with brand focus
python main.py generate \
  --mission "Promote our new sustainable products" \
  --platform instagram \
  --duration 30 \
  --style professional \
  --tone engaging \
  --visual-style cinematic
```

### Batch Processing
```bash
# Generate multiple videos with different parameters
for platform in instagram tiktok youtube; do
  python main.py generate \
    --mission "Daily motivation tip" \
    --platform $platform \
    --duration 15 \
    --mode professional
done
```

## Architecture Documents

- 📖 **[SYSTEM_ARCHITECTURE.md](SYSTEM_ARCHITECTURE.md)** - Complete technical architecture
- 🔄 **[CURRENT_FLOW.md](CURRENT_FLOW.md)** - Detailed system flow and operation
- 🔧 **[docs/](docs/)** - Additional documentation and guides

## Contributing

This is a production system with comprehensive AI integration. For modifications:

1. Review the centralized decision framework
2. Understand the AI agent system
3. Follow the session management patterns
4. Test with `--cheap full` mode first

## License

[License information]

---

**ViralAI** - *Where AI meets viral content creation* 🚀