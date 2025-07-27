# ViralAI System Architecture & Flow

## Overview

ViralAI is a comprehensive AI-powered video generation system that uses multiple AI agents, centralized decision-making, and advanced generation models to create viral content for social media platforms. The system now features a Universal AI Provider Interface that allows seamless switching between different AI providers (Gemini, Vertex AI, OpenAI, Anthropic) without code changes.

## Current Architecture (v3.2+)

### 1. **Centralized Decision Framework** 🎯

The system follows a **Decision-First Architecture** where all key decisions are made upfront before any generation begins.

```
CLI Input → Decision Framework → Core Decisions → All Components
```

**Key Components:**
- `DecisionFramework` - Central decision-making system
- `CoreDecisions` - Data structure containing all system decisions
- Decision sources: CLI, config files, AI agents, system defaults

**What Gets Decided:**
- Duration, platform, category, style, tone
- Voice strategy, clip structure, visual elements
- Technical settings (frame continuity, cheap mode)
- Content elements (hook, CTA, mission)

### 2. **Theme System** 🎨

The system includes a comprehensive theme management system:

**Theme Components:**
- Pre-built themes (News, Sports, Tech, Entertainment, University)
- Custom theme creation and management
- Logo overlay integration
- Brand consistency across videos
- Platform-specific optimizations

**University Theme Features:**
- Academic color palette and typography
- Automatic logo overlay positioning
- Educational content optimization
- Professional lower thirds and captions

### 3. **Multi-Agent Discussion System** 🤖

22 specialized AI agents collaborate to create optimal content:

**Core Creative Team (7 agents):**
- StoryWeaver, VisionCraft, PixelForge, CutMaster, AudioMaster, TrendMaster, StyleSavant

**Professional Extensions (15 agents):**
- MarketMind, BrandGuard, SocialSavvy, AudienceAce, VisualVibe, TypeTech, ColorCraft, MotionMaster, EngagePro, ViralVault, DataDive, ContentCraft, PlatformPro, CopyCoach, ThumbTech

**Discussion Topics:**
1. Script Strategy & Viral Optimization
2. Visual Composition & Technical Approach
3. Audio Production & Voice Strategy
4. Marketing Strategy & Brand Alignment
5. Visual Design & Typography Optimization
6. Engagement Optimization & Virality Mechanics
7. Platform-Specific Optimization & Copywriting

### 3. **Video Generation Pipeline** 🎬

**Generation Flow:**
```
Decision Framework → AI Discussions → Content Generation → Video Assembly → Social Media
```

**Key Stages:**
1. **Decision Making** - All parameters decided upfront
2. **AI Discussions** - Agents collaborate on strategy
3. **Script Generation** - Enhanced script processing with AI
4. **Video Generation** - VEO-2/VEO-3 or fallback generation
5. **Audio Generation** - Enhanced multilingual TTS
6. **Video Assembly** - Composition with subtitles and overlays
7. **Social Media Integration** - Auto-posting with hashtags

### 4. **Generation Models** 🚀

**Video Generation:**
- **VEO-2** (Primary): Google's Vertex AI VEO-2 model
- **VEO-3** (Premium): Advanced VEO-3 with native audio
- **Fallback**: FFmpeg-based generation for testing

**Audio Generation:**
- **Enhanced TTS**: Google Cloud Text-to-Speech
- **AI Voice Selection**: Intelligent voice strategy
- **Fallback**: gTTS for cheap mode

**Content Generation:**
- **Script Processing**: Gemini AI for script enhancement
- **Hashtag Generation**: AI-powered trending hashtags
- **Image Generation**: Gemini image generation (when needed)

### 5. **Session Management** 📁

**Session Structure:**
```
outputs/session_YYYYMMDD_HHMMSS/
├── decisions/           # All decisions made
├── discussions/         # AI agent discussions
├── scripts/            # Script versions
├── audio/              # Audio files
├── video_clips/        # Generated video clips
├── final_output/       # Final video
├── hashtags/           # Generated hashtags
├── logs/               # Comprehensive logs
└── metadata/           # Session metadata
```

### 6. **Platform Integration** 📱

**Supported Platforms:**
- TikTok, Instagram, YouTube, Twitter, LinkedIn

**Platform-Specific Features:**
- Aspect ratio optimization
- Duration constraints
- Content style adaptation
- Hashtag strategies
- Auto-posting capabilities

## System Flow

### 1. **Input Processing**
```bash
python main.py generate --mission "Your mission" --platform instagram --duration 10 --mode professional
```

### 2. **AI Provider Initialization** (NEW!)
```
AIServiceManager → AIServiceFactory → Provider Initialization
```
- Loads AI configuration from environment and config files
- Initializes selected providers for each service type
- Sets up fallback chains for reliability
- Validates API keys and credentials

### 3. **Decision Making Phase**
```
CLI Arguments → DecisionFramework.make_all_decisions() → CoreDecisions
```
- Analyzes CLI input, user config, and system defaults
- Makes all strategic decisions (duration, style, voice, clips)
- Records decision source and confidence
- Saves decisions to session

### 4. **AI Agent Discussions**
```
CoreDecisions → WorkingOrchestrator → MultiAgentDiscussion
```
- 7 comprehensive discussions with 22 agents
- Agents use core decisions to create strategies
- Consensus-based decision refinement
- Platform-specific optimizations

### 5. **Content Generation**
```
AI Strategies → Script Processing → Video/Audio Generation
```
- Enhanced script processing with AI
- Intelligent voice selection
- VEO-2/VEO-3 video generation
- Clip-based generation with precise durations

### 6. **Video Assembly**
```
Video Clips + Audio + Subtitles + Overlays → Final Video
```
- MoviePy-based video composition
- AI-driven subtitle positioning
- Dynamic overlays and hooks
- Platform-specific formatting

### 7. **Social Media Integration**
```
Final Video → Hashtag Generation → Auto-posting
```
- AI-generated trending hashtags
- Platform-specific posting
- Engagement optimization
- Analytics tracking

## Key Features

### ✅ **Centralized Decision Making**
- All parameters decided once upfront
- No conflicting decisions between components
- Full traceability of decision sources

### ✅ **22 AI Agents**
- Professional mode with comprehensive agent coverage
- Specialized roles for different aspects
- Consensus-based collaboration

### ✅ **Universal AI Provider Interface** (NEW!)
- Unified interface for all AI services (text, image, video, speech)
- Easy provider switching without code changes
- Support for multiple providers: Gemini, Vertex AI, OpenAI, Anthropic
- Automatic fallback and error handling
- Cost optimization through provider selection

### ✅ **Flexible Generation**
- Multiple generation models (VEO-2, VEO-3, fallback)
- Cheap mode for cost-effective testing
- Professional mode for production

### ✅ **Session Management**
- Comprehensive file organization
- Full audit trail of all operations
- Easy debugging and replay

### ✅ **Platform Optimization**
- Platform-specific adaptations
- Auto-posting capabilities
- Engagement optimization

## Technical Architecture

### Core Components

**Decision Layer:**
- `DecisionFramework` - Central decision system
- `CoreDecisions` - Decision data structure

**Configuration Layer:** (NEW!)
- `VideoGenerationConfig` - Master configuration class
- `VideoEncodingConfig` - Encoding parameters
- `TextOverlayConfig` - Text styling configuration
- `AnimationTimingConfig` - Animation and timing settings
- `DefaultTextConfig` - Default text templates
- `LayoutConfig` - Layout and positioning

**AI Provider Layer:** (NEW!)
- `UniversalAIProviderInterface` - Unified interface for all AI services
- `AIServiceManager` - Central manager for AI service access
- `AIServiceFactory` - Factory for creating AI service instances
- Provider adapters for Gemini, Vertex AI, OpenAI, Anthropic, Google Cloud

**Orchestration Layer:**
- `WorkingOrchestrator` - Main coordination
- `MultiAgentDiscussion` - Agent collaboration

**Generation Layer:**
- `VideoGenerator` - Video creation orchestration (uses VideoGenerationConfig)
- `VeoClientFactory` - Model selection and management
- `EnhancedMultilingualTTS` - Audio generation
- `EnhancedScriptProcessor` - Script processing with configuration awareness

**Platform Layer:**
- `InstagramAutoPoster` - Social media integration
- `HashtagGenerator` - Trending hashtag generation

### Data Flow

```
1. CLI Input → Decision Framework
2. Core Decisions → Working Orchestrator
3. AI Discussions → Generation Strategies
4. Content Generation → Video Assembly
5. Final Video → Social Media
```

### Session Context

Every operation is tracked in a session with:
- Complete decision log
- AI agent discussions
- Generation artifacts
- Comprehensive logs
- Performance metrics

## Configuration

### 🎛️ **Centralized Video Configuration System** (NEW!)

The system now features a comprehensive configuration module that eliminates ALL hardcoded values. Every aspect of video generation is configurable through a centralized system.

**Configuration Module:** `src/config/video_config.py`

#### Configuration Categories:

**1. Video Encoding Configuration (`VideoEncodingConfig`):**
- Platform-specific FPS settings (YouTube: 30fps, TikTok: 30fps, etc.)
- Video/audio codec settings (libx264, aac)
- Quality presets per platform (medium for YouTube, fast for TikTok)
- CRF values for quality control (23 for YouTube, 25 for TikTok)
- Fallback encoding settings for cheap mode

**2. Text Overlay Configuration (`TextOverlayConfig`):**
- Dynamic font sizing based on video dimensions (6% for titles, 4% for body)
- Minimum font sizes to ensure readability
- Stroke widths for text outlines
- Default colors and opacity settings
- Semi-transparent backgrounds (0.8 opacity)

**3. Animation Timing Configuration (`AnimationTimingConfig`):**
- Fade in/out durations (0.5s default)
- Display durations for hooks and CTAs (3.0s)
- Subtitle and overlay fade timings
- Frame continuity settings for seamless transitions
- Crossfade and transition durations

**4. Default Text Configuration (`DefaultTextConfig`):**
- Platform-specific hook texts
- Platform-specific CTA messages
- Badge texts for overlays
- News channel branding text

**5. Layout Configuration (`LayoutConfig`):**
- Subtitle positioning with theme awareness
- Overlay positioning and animations
- Safe zone calculations (5% margins)
- Text wrapping limits (90% for subtitles, 80% for overlays)
- Vertical spacing between elements (80px)

#### Configuration Usage:

```python
from src.config.video_config import video_config

# Get platform-specific settings
fps = video_config.get_fps('youtube')  # Returns 30
crf = video_config.get_crf('tiktok')   # Returns 25

# Calculate dynamic font sizes
font_size = video_config.get_font_size('title', 1920)  # Returns 115px for 1920 width

# Get platform-specific text
hook = video_config.get_default_hook('instagram')  # Returns "You won't believe this!"
```

### 🔌 **Universal AI Provider Interface** (NEW!)

The system now supports multiple AI providers through a unified interface:

**Supported Providers:**
- **Text Generation**: Gemini, Vertex AI, OpenAI, Anthropic
- **Image Generation**: Gemini, Vertex AI (Imagen)
- **Video Generation**: Gemini (VEO-2/VEO-3), Vertex AI
- **Speech Synthesis**: Google Cloud TTS, ElevenLabs (planned)

**Provider Configuration:**
```python
from src.ai.service_manager import AIServiceManager
from src.ai.interfaces.base import AIServiceType, AIProvider

# Get service manager instance
manager = AIServiceManager()

# Use specific provider
text_service = manager.get_service(
    AIServiceType.TEXT_GENERATION,
    provider=AIProvider.OPENAI
)

# Generate text
response = await text_service.generate_text(
    TextGenerationRequest(
        prompt="Create a viral video script",
        max_tokens=1000,
        temperature=0.7
    )
)
```

**Benefits:**
- Easy provider switching for cost optimization
- Automatic fallback handling
- Unified error handling across providers
- Consistent interface for all AI services
- Future-proof architecture for new providers

### Environment Variables
- `GOOGLE_AI_API_KEY` - Gemini API key
- `GOOGLE_CLOUD_PROJECT` - GCP project ID
- `GOOGLE_APPLICATION_CREDENTIALS` - Service account key

### CLI Options
- `--mission` - Video mission/topic
- `--platform` - Target platform
- `--duration` - Video duration (seconds)
- `--mode` - Generation mode (simple/enhanced/professional)
- `--cheap` - Cost-saving mode
- `--style` - Content style
- `--tone` - Content tone
- `--theme` - Theme preset (news, sports, tech, entertainment)
- `--style-template` - Saved style template name
- `--reference-style` - Path to reference video for style extraction
- `--character` - Character ID for consistent character generation
- `--scene` - Scene description when using character

### User Configuration
- `src/config/video_config.py` - Master video configuration
- Config files for default settings
- User preference overrides
- Platform-specific configurations

## Performance & Scaling

### Cost Optimization
- Cheap mode with text-based generation
- Granular cheap mode levels (full/audio/video)
- Fallback generation for testing

### Quality Modes
- **Simple**: Basic generation with minimal AI
- **Enhanced**: 7 agents with discussions
- **Professional**: 22 agents with comprehensive discussions

### Monitoring
- Comprehensive logging system
- Performance metrics tracking
- Session-based debugging
- Error handling and recovery

## Security & Privacy

### Authentication
- Google Cloud IAM integration
- Secure API key management
- Auto-authentication setup

### Data Handling
- Session-based file organization
- Secure credential storage
- No sensitive data in logs

### Platform Integration
- Secure Instagram authentication
- Token-based API access
- Rate limiting and quota management

---

*This architecture provides a scalable, maintainable, and feature-rich system for AI-powered video generation with comprehensive social media integration.*