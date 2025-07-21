# ViralAI - AI-Powered Video Generation System

🚀 **Production-ready AI video generation system with 22 specialized agents, centralized decision-making, and comprehensive social media integration.**

[![Version](https://img.shields.io/badge/version-2.5.0--rc2-blue.svg)](https://github.com/yourusername/viral-video-generator/releases/tag/v2.5.0-rc2)
[![Status](https://img.shields.io/badge/status-Production%20Ready-green.svg)](https://github.com/yourusername/viral-video-generator)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)

## ✨ **What's New in v2.5.0-rc2**

### 🎬 **Multiple Video Versions**
- **Three Output Versions**: Final (with subtitles/overlays), Audio Only, Overlays Only
- **Maximum Flexibility**: Choose the version that best fits your needs
- **Editing Freedom**: Clean versions for custom modifications
- **Multi-Platform Ready**: Different versions for different platforms
- **Language Versatility**: Easy to add custom subtitles to clean versions

### 🎨 **Enhanced Styling System**
- **Improved Font Selection**: Professional fonts (Helvetica-Bold, Arial-Bold, Impact, Georgia-Bold)
- **Sophisticated Color Palette**: No more redundant orange - uses coral red, turquoise, sky blue, mint green, purple, cyan, rose
- **AI-Powered Typography**: Intelligent font and color selection based on content type
- **Better Visual Hierarchy**: Enhanced text overlays with improved readability

### 🚨 **Critical Bug Fixes**
- **Fixed**: DiscussionResult object handling causing video generation crashes
- **Fixed**: Type safety issues in video generation pipeline
- **Fixed**: Return type annotations and error handling
- **Enhanced**: System reliability and error recovery

### 🎯 **Perfect Subtitle Synchronization**
- **Auto-Calibrating Timing**: Adapts to gTTS and premium TTS automatically
- **Word-Level Precision**: Calculates timing based on actual word count
- **Real Audio Analysis**: Syncs to actual audio duration, not theoretical
- **Natural Pauses**: Intelligent pause detection between sentences

### 🕐 **Duration-Aware AI Agents**
- **Hard Duration Constraints**: AI agents respect exact time limits
- **Smart Content Scaling**: Automatically adjusts content to fit duration
- **Word Count Limits**: Uses 2.8-3.2 words/second speaking rate constraints
- **Script Completion**: Ensures full story within time bounds

### 🎭 **Enhanced Voice System**
- **Single Voice Preference**: Professional single-voice narration by default
- **Multi-Speaker Detection**: Intelligent detection for dialogue and interviews
- **Voice Boundary Protection**: Never switches voice mid-sentence
- **Context-Aware Selection**: Contextually appropriate voice selection

### 🎨 **100+ Visual Styles**
- **Photographic**: realistic, cinematic, documentary, portrait, macro
- **Artistic**: watercolor, oil painting, impressionist, cubist, abstract
- **Animation**: Disney, Pixar, anime, comic book, claymation
- **Cultural**: Japanese, Egyptian, Celtic, Persian, African
- **Technical**: blueprint, wireframe, x-ray, holographic, glitch

### 🔧 **Production-Ready Features**
- **Robust Session Management**: Auto-recovery and error handling
- **Instagram Integration**: Real API posting with instagrapi
- **Multi-Language Support**: 10+ languages with RTL rendering
- **Professional Quality**: Studio-grade audio and HD video output

## Quick Start

### Prerequisites
- Python 3.8+
- Google Cloud Project with Vertex AI enabled
- Google AI API key

### 🚀 **Latest Release: v2.5.0-rc2**
- **Critical Bug Fixes**: Fixed DiscussionResult object handling causing system crashes
- **Enhanced Type Safety**: Improved error recovery and system stability
- **Production Ready**: All critical issues resolved for production deployment

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
# Generate a professional video with 22 AI agents (creates 3 versions)
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
  --visual-style cinematic

# Use artistic visual styles
python main.py generate \
  --mission "Art tutorial for beginners" \
  --platform youtube \
  --duration 45 \
  --visual-style watercolor \
  --mode professional

# Cultural-themed content
python main.py generate \
  --mission "Traditional Japanese tea ceremony" \
  --platform instagram \
  --duration 30 \
  --visual-style japanese \
  --tone respectful

# Cost-effective testing mode
python main.py generate \
  --mission "Test content creation" \
  --platform youtube \
  --duration 20 \
  --cheap full
```

### 🎬 **Multiple Video Versions Output**
Every generation creates three versions automatically:

```bash
# Example output files for session_20250721_123456:
outputs/session_20250721_123456/final_output/
├── final_video_session_20250721_123456_final.mp4      # Complete version
├── final_video_session_20250721_123456_audio_only.mp4 # Clean version
└── final_video_session_20250721_123456_overlays_only.mp4 # Overlays only

# Summary files:
outputs/session_20250721_123456/metadata/
├── video_versions_summary.json  # Machine-readable metadata
└── video_versions_summary.md    # Human-readable documentation
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

## 🎨 **Visual Styles (100+ Options)**

### Photographic & Realistic
```bash
--visual-style realistic        # Photorealistic, high quality
--visual-style cinematic        # Cinematic lighting, dramatic
--visual-style documentary      # Authentic, real-world settings
--visual-style portrait         # Professional portrait photography
--visual-style macro            # Extreme close-ups, fine details
--visual-style golden_hour      # Warm sunset lighting
--visual-style neon            # Neon lighting, urban nightlife
```

### Animation & Cartoon
```bash
--visual-style disney          # Disney animation style
--visual-style pixar           # Pixar 3D animation
--visual-style anime           # Japanese animation style
--visual-style comic_book      # Comic book illustration
--visual-style claymation      # Clay animation, tactile
--visual-style stop_motion     # Stop motion animation
```

### Artistic & Painting
```bash
--visual-style watercolor      # Watercolor painting style
--visual-style oil_painting    # Rich textures, classical art
--visual-style impressionist   # Light and color, loose brushstrokes
--visual-style cubist          # Geometric shapes, multiple perspectives
--visual-style pop_art         # Bold colors, commercial imagery
--visual-style abstract        # Non-representational, conceptual
```

### Cultural & Historical
```bash
--visual-style japanese        # Traditional Japanese aesthetics
--visual-style egyptian        # Ancient Egyptian symbols
--visual-style celtic          # Celtic knots, mystical
--visual-style persian         # Intricate carpets, miniatures
--visual-style aztec           # Geometric patterns, ancient civilization
--visual-style viking          # Norse mythology, runic symbols
```

### Genre & Thematic
```bash
--visual-style cyberpunk       # Futuristic, neon, high-tech
--visual-style steampunk       # Victorian era, brass and gears
--visual-style horror          # Dark, scary, unsettling
--visual-style noir            # High contrast, shadows, mystery
--visual-style synthwave       # 80s neon, outrun aesthetic
--visual-style cottagecore     # Rural, cozy, natural
```

### Technical & Material
```bash
--visual-style blueprint       # Technical drawings, architectural
--visual-style wireframe       # Technical, blueprint-like
--visual-style holographic     # Rainbow effects, futuristic
--visual-style glitch          # Digital corruption, cyberpunk
--visual-style crystal         # Geometric, magical textures
--visual-style microscopic     # Cellular, scientific detail
```

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