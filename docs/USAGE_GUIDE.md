# 📖 Enhanced Viral Video Generator - Usage Guide

## 🎯 AI-Powered Topic Generation

Transform high-level ideas into optimized video topics using 6 specialized AI agents.

### Basic Topic Generation
```bash
python3 main.py generate-topic --idea "convince people to vote"
```

### Advanced Topic Generation
```bash
python3 main.py generate-topic \
  --idea "promote environmental awareness" \
  --platform youtube \
  --audience "Young adults" \
  --style "Educational" \
  --duration 60 \
  --category Educational
```

### Auto-Generate Video
```bash
python3 main.py generate-topic \
  --idea "encourage healthy eating" \
  --generate-video
```

## 🎬 Video Generation

### Basic Video Generation
```bash
python3 main.py generate --topic "Quick fitness tips for busy people" --duration 30
```

### Advanced Video Generation
```bash
python3 main.py generate \
  --topic "AI revolutionizing content creation" \
  --duration 60 \
  --category Educational \
  --platform youtube \
  --discussions deep \
  --frame-continuity auto
```

## 🌐 Web Interface

### Launch UI
```bash
python3 simple_test_ui.py
# Access at http://localhost:7860
```

### UI Features
- **🎯 Topic Generation Tab**: AI-powered topic creation
- **🎬 Video Generation Tab**: Complete video production
- **❓ Help Tab**: Comprehensive documentation

## 🤖 AI Agent System

### Discussion Modes
- **Light**: 1-2 rounds, quick consensus
- **Standard**: 2-3 rounds, balanced quality
- **Deep**: 3-4 rounds, maximum quality

### Frame Continuity Options
- **Auto**: AI decides based on content (recommended)
- **On**: Smooth transitions between clips
- **Off**: Jump cuts for dynamic pacing

### Platform Optimization
Each platform has specific optimizations:
- **YouTube**: Educational, longer content, smooth transitions
- **TikTok**: Viral, short, jump cuts, trending elements
- **Instagram**: Visual-first, engagement hooks
- **Twitter**: Concise, trending topics, shareability

## 📊 Session Management

### Output Structure
```
outputs/session_YYYYMMDD_HHMMSS_sessionid/
├── final_video_sessionid.mp4           # Generated video
├── google_tts_voice_uuid.mp3           # Audio file
├── comprehensive_logs/                 # System logs
├── agent_discussions/                  # AI discussions
├── composition_discussions/            # Advanced composition
└── session_summary.md                 # Human-readable summary
```

### Viewing Results
```bash
# List recent sessions
ls -la outputs/session_*/

# View session summary
cat outputs/session_YYYYMMDD_HHMMSS_sessionid/session_summary.md
```

## 🎨 Customization Options

### Video Categories
- **Comedy**: Humorous, entertaining content
- **Educational**: Informative, instructional
- **Entertainment**: General entertainment
- **News**: Current events, updates
- **Technology**: Tech-focused content

### Duration Guidelines
- **10-15 seconds**: TikTok, Instagram Reels
- **30-60 seconds**: YouTube Shorts, general social media
- **60+ seconds**: YouTube, educational content

## 🔍 Monitoring and Analytics

### Discussion Analysis
```bash
# View recent discussions
python3 main.py discussions --recent 5

# Analyze specific session
python3 main.py discussions --session-id SESSIONID
```

### Quota Monitoring
```bash
# Check API quotas
python3 main.py veo-quota
```

## 💡 Best Practices

### Topic Generation Tips
1. **Be Specific**: "convince young adults to vote in local elections" vs "get people to vote"
2. **Include Context**: Specify target audience and platform
3. **Consider Ethics**: AI agents will ensure responsible messaging

### Video Generation Tips
1. **Match Duration to Platform**: Short for TikTok, longer for YouTube
2. **Use Appropriate Categories**: Match content type to category
3. **Let AI Decide Frame Continuity**: Auto mode usually works best

### Performance Optimization
1. **Use Light Discussions**: For faster generation during testing
2. **Standard Mode**: Best balance of speed and quality
3. **Deep Discussions**: For final, high-quality content

## 🚨 Troubleshooting

### Common Issues
- **Slow Generation**: Try light discussion mode
- **Poor Audio Quality**: Ensure Google Cloud TTS is configured
- **Low Viral Potential**: Use topic generation for optimized topics
- **Platform Mismatch**: Ensure platform settings match your target

### Error Resolution
1. Check console output for detailed error messages
2. Verify API keys and quotas
3. Ensure proper file permissions for outputs/
4. Restart if memory issues occur

## 📈 Advanced Features

### Multi-Agent Discussions
- 26+ specialized AI agents
- Senior Manager supervision
- Real-time consensus building
- Comprehensive decision logging

### Intelligent Composition
- AI-powered video structure decisions
- VEO2 vs static image selection
- Optimized text overlay positioning
- Platform-specific optimizations 