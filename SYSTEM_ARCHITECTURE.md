# ViralAI System Architecture & Flow

## Overview

ViralAI is a comprehensive AI-powered video generation system that uses multiple AI agents, centralized decision-making, and advanced generation models to create viral content for social media platforms.

## Current Architecture (v2.5+)

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

### 2. **Multi-Agent Discussion System** 🤖

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

### 2. **Decision Making Phase**
```
CLI Arguments → DecisionFramework.make_all_decisions() → CoreDecisions
```
- Analyzes CLI input, user config, and system defaults
- Makes all strategic decisions (duration, style, voice, clips)
- Records decision source and confidence
- Saves decisions to session

### 3. **AI Agent Discussions**
```
CoreDecisions → WorkingOrchestrator → MultiAgentDiscussion
```
- 7 comprehensive discussions with 22 agents
- Agents use core decisions to create strategies
- Consensus-based decision refinement
- Platform-specific optimizations

### 4. **Content Generation**
```
AI Strategies → Script Processing → Video/Audio Generation
```
- Enhanced script processing with AI
- Intelligent voice selection
- VEO-2/VEO-3 video generation
- Clip-based generation with precise durations

### 5. **Video Assembly**
```
Video Clips + Audio + Subtitles + Overlays → Final Video
```
- MoviePy-based video composition
- AI-driven subtitle positioning
- Dynamic overlays and hooks
- Platform-specific formatting

### 6. **Social Media Integration**
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

**Orchestration Layer:**
- `WorkingOrchestrator` - Main coordination
- `MultiAgentDiscussion` - Agent collaboration

**Generation Layer:**
- `VideoGenerator` - Video creation orchestration
- `VeoClientFactory` - Model selection and management
- `EnhancedMultilingualTTS` - Audio generation

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

### User Configuration
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